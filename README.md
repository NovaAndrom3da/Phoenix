# ⚡ Phoenix ⚡
Phoenix is a speedy lightweight web server with support for modules and extensions.

## 📦 Installation 📦
You can quickly and easily install from PyPi by running:
```bash
pip install phoenix-ws
```

This provides you with the Phoenix server and PPM package manager.

## 😀 How it works 😀
Phoenix quickly reads all of the files used by the server and caches them. This reduces the amount of disk read-write operations. It then delivers the files using gzip and zlib to reduce packet size.

Phoenix uses a very small amount of RAM, making it perfect for production environments.

## 🏁 Getting Started 🏁
You can quickly run Phoenix with:
```bash
phoenix run
```

## ⚙ Configuration ⚙
### Command Line Configuration
#### `run`
> `--host` `-h` - Allow the server to be publicly accessible from other devices.
>
> `--port <port>` `-p <port>` - Specify the port to run the server on.

#### `install <package>`
> 

### Project File Configuration
Phoenix can be configured per-project with a `phoenix.config.json` file. Here are the options:

> `host` (`bool`, `false`) - Allow the server to be publicly accessible from other devices.
> 
> `port` (`int`, `8080`) - Specify the port to run the server on.
>
> `zlib` (`bool`, `true`) - Use zlib compression.
>
> `gzip` (`bool`, `true`) - Use gzip compression.
>
> `verbose` (`bool`, `false`) - Print extra debug messages to the console.
>
> `indexDirectories` (`bool`, `false`) - Display the directory's contents if no file is specified.
>
> `indexPhoenix` (`bool`, `false`) - Index the `/phoenix/` directory.
>
> `encoding` (`str`, `utf-8`) - Set the text encoding.
>
> `nocompress` (`list`, `[]`) - Disable compression on specific files. Each item of the list is the resource's URL.
>
> `minify` (`bool`, `true`) - Make HTML, CSS, and JS files smaller.
>
> `proxy` (`dict`, `{}`) - Reverse-proxy websites.
>
> `fixProxy` (`bool`, `true`) - Replace all instances of the proxied URL with the requested URL.
>
> `thisURL` (`str`) - A nice name for the website hosted by the server. Used for `fixProxy`.
