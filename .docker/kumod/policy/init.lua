local kumo = require 'kumo'

kumo.on('init', function()
    -- Listen on port 2525 for incoming mail
    kumo.start_esmtp_listener {
        listen = '0:2525',
        relay_hosts = { '0.0.0.0/0' },
    }

    kumo.define_spool {
        name = 'data',
        path = '/tmp/kumo-sink/data',
    }

    kumo.define_spool {
        name = 'meta',
        path = '/tmp/kumo-sink/meta',
    }

    kumo.configure_local_logs {
        log_dir = '/var/log/kumomta',
        max_segment_duration = '10 seconds',
        headers = { 'Subject', 'Message-ID' },
        per_record = {
            Any = {
                enable = true,
            },
        },
    }
end)

-- Configure listener domains using external TOML file
local listener_domains = require 'policy-extras.listener_domains'

kumo.on(
    'get_listener_domain',
    listener_domains:setup { '/opt/kumomta/etc/listener_domains.toml' }
)

-- Configure HTTP delivery for everything
kumo.on('get_queue_config', function(domain, tenant, campaign, routing_domain)
    return kumo.make_queue_config {
        protocol = {
            custom_lua = {
                constructor = 'make.webhook',
            },
        },
    }
end)

-- HTTP delivery handler
kumo.on('make.webhook', function(domain, tenant, campaign)
    local connection = {}
    local client = kumo.http.build_client {}

    function connection:send(message)
        local api_uri = 'https://kumod.requestcatcher.com/'

        -- Prep message data
        local email_data = message:get_data()
        local recipient = message:recipient()
        local sender = message:sender()
        local to_email = recipient.email
        local from_email = tostring(sender) -- Convert sender to string

        -- Prepare JSON payload with email meta and RAW message
        local payload = {
            to = to_email,
            from = from_email,
            subject = message:get_first_named_header_value('Subject') or '',
            message_id = message:get_first_named_header_value('Message-ID'),
            raw_message = tostring(email_data), -- Ensure it's a string
            domain = domain,
            timestamp = os.time(),
        }

        -- Convert payload to JSON (with error handling)
        local json_payload
        local success, result = pcall(kumo.json_encode, payload)
        if success then
            json_payload = result
        else
            -- Error payload
            json_payload = string.format('{"error":"JSON encoding failed: %s","to":"%s","from":"%s"}',
                result, to_email, from_email)
        end

        -- Make HTTP POST request to webhook
        local request = client:post(api_uri)
        request:header('Content-Type', 'application/json')
        request:body(json_payload)

        local response = request:send()

        -- Create disposition message
        local disposition = string.format(
            '%d %s: %s',
            response:status_code(),
            response:status_reason(),
            response:text()
        )

        if response:status_is_success() then
            return disposition
        end

        -- Failure will retry or bounce
        kumo.reject(400, disposition)
    end

    function connection:close()
        client:close()
    end

    return connection
end)
