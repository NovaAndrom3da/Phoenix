# ⚡ Pheonix ⚡
Pheonix is a speedy lightweight web server with support for modules and extensions.

## 📦 Installation 📦
You can quickly and easily install from PyPi by running:
```bash
pip install pheonix
```

This provides you with the Pheonix server and PPM package manager.

## 😀 How it works 😀
Pheonix quickly reads all of the files used by the server and caches them. This reduces the amount of disk read-write operations. It then delivers the files using gzip and zlib to reduce packet size.

Pheonix uses a very small amount of RAM, making it perfect for production environments.

## 🏁 Getting Started 🏁
You can quickly run Pheonix with:
```bash
pheonix run
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
Pheonix can be configured per-project with a `pheonix.config.json` file. Here are the options:

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
> `indexPheonix` (`bool`, `false`) - Index the `/pheonix/` directory.
>
> `encoding` (`str`, `utf-8`) - Set the text encoding.
>
> `nocompress` (`list`, `[]`) - Disable compression on specific files. Each item of the list is the resource's URL.
> 
> `purgecache` (`bool`, `true`) - Clear the excess cache.
>
> `minify` (`bool`, `true`) - Make HTML, CSS, and JS files smaller.
>
> `proxy` (`dict`, `{}`) - Reverse-proxy websites.
>
> `fixProxy` (`bool`, `true`) - Replace all instances of the proxied URL with the requested URL.
>
> `thisURL` (`str`) - A nice name for the website hosted by the server. Used for `fixProxy`.
> 
> `canrebuild` - WIP
