>本文是Hexo自动更新脚本的使用说明。

##环境准备

1. HexoUp目前只支持OSX及Linux（未验证）环境。
2. Python运行环境。
3. SSH需要支持免密码登陆（参考：http://www.cnblogs.com/tankaixiong/p/4172942.html）。

##修改配置文件

程序首次执行时，如果没有预先配置`hexoup.cfg`（位于用户目录下的.hexoup文件夹）将不会继续执行并自动生成hexoup.cfg文件。
hexoup.cfg的配置如下:

	[ssh]
	name = SSH用户名
	server = SSH服务器地址
	
	[path]
	locale = 本地的博客目录，该目录下的所有文档都会被处理，所有以`.`开始的文件会被自动忽略
	remote = 服务器端的博客目录，一般为hexo目录下的source/_post文件夹

##指定分类和标签

使用这个功能有个前提，即：你需要明确的知道每个文档目录下对应的文档应该是同一类型的。

HexoUp会自动解析文档根目录中所包含的所有目录下的`.tags`、`.categories`文件。每个`.tags`、`.categories`文件中的每一行文本对应一个标签或分类。举例说明：

![](http://7xifbq.com1.z0.glb.clouddn.com/14511967257324.jpg)

上图中`.tags`文件同时出现在三个目录中，文件中分别有文本内容：`Android`、`笔记`、`Activity`。HexoUp在生成临时文档时会将这三个文本内容分别加入到`Activity生命周期`、`Activity启动模式`，`IntentFilter匹配规则`这三篇文档中。


##工作目录

HexoUp会在`hexoup.cfg`文件中制定的locale目录下生成一个`.work`工作目录。HexoUp最终会将该工作目录下符合要求的文档更新到Hexo服务器。

##执行脚本

有多种方式执行脚本：

1. 直接通过以下命令执行：
	
		python hexoup.py
	
	执行上述命令前需要先进去到hexoup.py文件所在的目录。
	
2. 通过bash命令调用：
	* 新建一个文件夹，如hexoup，并将hexoup.py文件复制到这个文件夹内；
	* 新建一个可执行的bash文件，如hexoup，写入以下代码并保存：
	
			#! /usr/bin/env bash
	
			CMD_PATH=`dirname $0`
			cd $CMD_PATH
			python "$PWD/hexoup.py"
			read -n1 -p "Press any key to exit."
	
	* 对hexoup文件赋予可执行权限：
	
			chmod a+x hexoup
	
	需要上传博客的时候执行双击`hexoup`文件就可以了。


##已知问题

Next主题似乎对分类的支持不是很好，当前版本的HexoUp暂时屏蔽了分类相关的代码实现。

