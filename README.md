# 百词斩单词释义 API

最近在背英语单词, 想要给英语单词标上释义. 最好有中英双语的.

网络上翻译单词的接口很多, 可大多数都是纯粹的英翻中, 需要用多个接口才能做到中英双语解释.

而且很多接口的返回数据过于简单或过于详细... 比如...

```
# 有道翻译 API
average
- n. 平均；平均数；（海损的）平均分担；平均水平；（按保单规定应付赔偿额的）降减
- adj. 平均（数）的；普通的；典型的；平庸的；中等的，适中的
- v. 算出……的平均数；将……平均分配；使……平衡；平均为，平均达到；呈中间色；（行情下跌时）买进更多的证券（或商品）以降低平均进价

# 谷歌翻译 API(网页版)
average
- 平均

# 百词斩翻译
average
- n. 平均数；平均水平
- adj. 通常的；一般的；平均的
- vt. 平均为

the result of adding several amounts together, finding a total, and dividing the total by the number of amounts

例句: His height equals the average of his parents' heights.
```

比较来看相对来说百词斩的解释比较详略得当.(还附赠了英文释义).

受到 [https://github.com/KarasuShing/parseZpk](https://github.com/KarasuShing/parseZpk) 这个项目的启发, 写了一个程序解析百词斩的 zpk 文件来做一个百词斩单词释义 API.

p.s. 本 API 只提供**单词和部分短语的释义**, 翻译句子的话还是需要使用其他翻译 API.

并且不打算解析 zpk 文件中的音频和图片. 音频如果需要的话可以通过其他 tts API 获取.

至于百词斩的配图个人觉得没有很大帮助, 解析出来占用太多储存空间.

## API 使用说明

其实本来这只是一个 zpk 解析脚本, 但为了使用方便我已经将常用的单词解析好放到了 Github 仓库里, 就成了这个 API.

所有的单词数据更新于 2021/1/1, 共 10927 条. 国内建议使用 jsDelivr CDN 访问.

### 获取所有单词列表

#### Request

- Method: Get
- URL: https://cdn.jsdelivr.net/gh/lyc8503/baicizhan-word-meaning-API/data/list.json

#### Response

```json
{"total": 10927,
 # 下面这个 list 里就是所有单词
 "list":["a", "b", "c", ...]}
```

### 获取单个单词释义

#### Request

- Method: GET

- URL: https://cdn.jsdelivr.net/gh/lyc8503/baicizhan-word-meaning-API/data/words/[WORD].json

  其中将 [WORD] 是将上面 list 中的**单词或短语中 `/ \ : * ? " < > |` 这些符号**和**短语中的空格**替换为**下划线**之后得到的值.

  获取 [WORD] 的参考代码. (python)

  ```python
  import re
  # word 变量是 list 中的一个单词或短语
  
  # 替换不合法文件名
  rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
  word = re.sub(rstr, "_", word)
  # 替换空格
  word = key.replace(" ", "_")
  
  # 下面开始发起请求
  ```

#### Response(以单词 average 为例)

```json
{
    # 英文单词
	"word": "average",
    # 音标
	"accent": "/\u02c8\u00e6v\u0259r\u026ad\u0292/",
    # 中文意思
	"mean_cn": "n.\u5e73\u5747\u6570\uff1b  adj.\u901a\u5e38\u7684\uff1b  vt.\u5e73\u5747\u4e3a",
    # 英文解释(可能为空字符串, 但绝大多数单词有英文解释.)
	"mean_en": "the result of adding several amounts together, finding a total, and dividing the total by the number of amounts",
    # 英文例句(可能为空字符串, 但大部分单词有例句.)
	"sentence": "His height equals the average of his parents' heights.",
    # 英文例句翻译
	"sentence_trans": "\u4ed6\u7684\u8eab\u9ad8\u7b49\u4e8e\u4ed6\u7236\u6bcd\u8eab\u9ad8\u7684\u5e73\u5747\u6570\u3002",
    # 相关的短语(可能为空字符串)
	"sentence_phrase": "the average of",
    # 单词词源(可能为空字符串)
	"word_etyma": "",
    # 一些其他数据(可能为空)
	"cloze_data": {
		"syllable": "av-er-age",
		"cloze": "av-er-a[ge]",
		"options": ["gue|dge|geo|dj"],
		"tips": [
			["a[ge]", "ima[ge]"]
		]
	}
}
```

## 本地构建方法

本 API 只收录了百词斩热门书中的词汇和短语. (中高考、四六级、考研、专升本、雅思托福).

如果你需要没有收录的单词(专四专八、小学、新概念等), 可以按照下面的方法自己在本地运行程序并导入需要的词汇.

1. git clone 该项目到本地.

2. 在安卓手机 / 安卓虚拟机上安装百词斩 APP, 下载所有你需要的单词书.

3. 打开 `安卓内部储存/Android/data/com.jiongji.android.card/files/baicizhan/zpack` 目录, 把整个目录复制到这个项目的 `zpk` 文件夹中.

   p.s. 读取过程中可能会有一些错误提示, 但是会自动用另一种方式重试.

   最终结果以最后一行输出为准. 没有发生错误或者错误数很少即代表解析成功.

4. 使用 python3 运行 main.py

5. 程序会在运行目录下生成 `data_<当前时间戳>`文件夹, 在该目录下搭建一个静态 HTTP 服务器即可使用.

   (如果只是临时使用可以直接在该目录下运行 `python3 -m http.server <端口号>`)

6. API 使用方法同上, 将服务器地址换成你自己的 HTTP 服务器地址即可.

