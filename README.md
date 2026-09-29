# BasicPortScanner v2.0

A fast, multi-threaded TCP port scanner written in pure Python 3 (no external dependencies).

## Features
- Multi-threaded scanning (hundreds of ports in parallel)
- Flexible port selection: `22,80,443`, `1-1024`, `top` (common ports), `all` (1-65535)
- Hostname resolution (IP address or domain name)
- Service name detection and optional banner grabbing
- Save results to a file
- Interactive menu when run without arguments
- Colored output, progress indicator and scan duration

## Download
_git clone https://github.com/CybercClay/BasicPortScanner-v2.0.git_

## Usage
Interactive mode:
```
python3 scanner.py
```

Command-line mode:
```
python3 scanner.py <target> [-p PORTS] [-t THREADS] [--timeout SEC] [-b] [-o FILE] [--no-color]
```

| Option | Description | Default |
|---|---|---|
| `-p, --ports` | Ports: `22,80,443`, `1-1024`, `top`, `all` | `1-1000` |
| `-t, --threads` | Number of concurrent threads | `200` |
| `--timeout` | Connection timeout in seconds | `1.0` |
| `-b, --banner` | Grab service banners from open ports | off |
| `-o, --output` | Save results to a file | – |
| `--no-color` | Disable colored output | – |

Examples:
```
python3 scanner.py scanme.nmap.org -p top
python3 scanner.py 192.168.1.1 -p 1-65535 -t 500 --timeout 0.5
python3 scanner.py 10.0.0.5 -p 22,80,443,8000-8100 -b -o results.txt
```

> Only scan systems you own or have explicit permission to test.

> if it doesn't work or if you want to contact me: selim.seven77@gmail.com
