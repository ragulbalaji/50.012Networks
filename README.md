Setup
-----

Use Reno congestion control instead of cubic:

    echo "reno" > /proc/sys/net/ipv4/tcp_congestion_control

Troubleshooting
---------------

Check which congestion control algorithm is in use:

    cat /proc/sys/net/ipv4/tcp_congestion_control

Check which congestion control algorithms are available:

    cat /proc/sys/net/ipv4/tcp_available_congestion_control 

Check that window scaling is enabled:

    cat /proc/sys/net/ipv4/tcp_window_scaling
