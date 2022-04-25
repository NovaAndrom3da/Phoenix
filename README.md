# ⚡ NoJS ⚡
NoJS is a speedy lightweight web server with support for modules and extensions.

## 📦 Installation 📦
You can quickly and easily install from PyPi by running:
```bash
pip install nopm
```

This provides you with the NoJS server and NoPM package manager.

## 😀 How it works 😀
NoJS quickly reads all of the files used by the server and caches them. This reduces the amount of disk read-write operations. It then delivers the files using gzip and zlib to reduce packet size.

NoJS uses a very small amount of RAM, making it perfect for production environments.

## 🏁 Getting Started 🏁
As of 04/25/2022, NoJS and NoPM does not yet support commandline operations. You can still start the server in Python:
```py
import nojs
nojs.run()
```

## ⚙ Configuration ⚙
NoJS can be configured per-project with a `nojs.config.json` file. Here are the options:

> `host` (`bool`, `false`) - Allow the server to be accessible to be accessible from other devices.
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
> `indexNoJS` (`bool`, `false`) - Index the `/nojs/` directory.
>
> `encoding` (`str`, `utf-8`) - Set the text encoding.
>
> `nocompress` (`list`, `[]`) - Disable compression on specific files. Each item of the list is the resource's URL.
> 
> `purgecache` (`bool`, `true`) - Clear the excess cache.
>
> `minify` (`bool`, `true`) - Make HTML, CSS, and JS files smaller.
> 
> `canrebuild` - WIP