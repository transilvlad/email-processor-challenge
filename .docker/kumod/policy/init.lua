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
