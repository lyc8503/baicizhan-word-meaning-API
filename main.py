import os
import logging
import json
import re
import time

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO)

all_files = []
all_data = []
all_data_dict = {}
fail_count = 0

logging.info("正在遍历 zpk 文件夹...")

# 遍历 zpk 文件夹
for dirpath, dirnames, filenames in os.walk("zpk"):
    for filename in filenames:
        if filename.endswith(".zpk"):
            filepath = os.path.join(dirpath, filename)
            all_files.append(filepath)

logging.info("遍历完成, 找到 " + str(len(all_files)) + " 个 zpk 文件.")


def read_zpk(path):
    f = open(path, "rb")

    # 大部分 zpk 的 json 在开头, 并且不会特别长, 只要读 4096 就够了
    # 但小部分 zpk 的 json 在结尾, 此时调用 read_zpk_full 暴力查找全文. (比较消耗资源...)
    content = f.read(4096).decode("utf-8", errors="ignore")
    start = content.find("{\"")

    # 没有找到 json 开头返回 None
    if start == -1:
        return None

    # 去除开头前面的部分
    # 查找 json 结尾: 用 "} 分割, 依次连接尝试还原 json
    slices = content[start:].split("\"}")

    for i in range(1, len(slices)):
        data = "\"}".join(slices[0:i])
        data += "\"}"

        try:
            return json.loads(data)
        except:
            pass


# 暴力匹配 zpk 文件中的 json. (作为 fallback)
def read_zpk_all(path):
    f = open(path, "rb")
    content = f.read(40960000).decode("utf-8", errors='ignore')

    start_indexes = []
    end_indexes = []

    for i in re.finditer("{", content):
        start_indexes.append(i.span()[0])
    for i in re.finditer("}", content):
        end_indexes.append(i.span()[0])

    all_poss = []

    # 尝试所有闭合的大括号组合
    for start in start_indexes:
        for end in end_indexes:
            if end > start:
                try:
                    # print(content[start:end])
                    all_poss.append(json.loads(content[start:end + 1]))
                except Exception as e:
                    # print("attempt fail", e)
                    pass

    if len(all_poss) == 0:
        return None

    # 返回最长的结果
    all_poss.sort(key=lambda x: len(str(x)), reverse=True)
    return all_poss[0]


for i in all_files:
    logging.info("读取: " + i)
    try:
        data = read_zpk(i)
        logging.info("读取单词成功: " + data['word'])
        all_data.append(data)
        continue
    except Exception as e:
        logging.warning("读取时出现错误, 尝试另一种读取方式: " + str(e))

    try:
        data = read_zpk_all(i)
        logging.info("重试时读取单词成功: " + data['word'])
        all_data.append(data)
    except Exception as e:
        logging.error("读取文件时发生错误, 无法恢复, 已跳过该文件: " + str(e))
        fail_count += 1

logging.info("所有 zpk 文件读取完成, 发生了 " + str(fail_count) + " 次不可恢复的错误.")
logging.info("获取到 " + str(len(all_data)) + " 条数据.")

logging.info("正在写入文件...")

while len(all_data) > 0:
    entry = all_data.pop()
    all_data_dict[entry['word']] = entry

logging.info("去除重复后有 " + str(len(all_data_dict)) + " 条数据.")

output_path = "data_" + str(round(time.time()))
os.mkdir(output_path)
os.chdir(output_path)
os.mkdir("words")

word_index = []
for key in all_data_dict:
    try:
        word_index.append(key)
        entry = all_data_dict[key]

        # 替换不合法文件名
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        key = re.sub(rstr, "_", key)

        # 替换空格
        key = key.replace(" ", "_")

        # 构造 json
        output_json = json.loads("{}")
        output_json['word'] = entry['word']
        output_json['accent'] = entry['accent']
        output_json['mean_cn'] = entry['mean_cn']

        try:
            output_json['mean_en'] = entry['mean_en']
        except Exception as e:
            output_json['mean_en'] = ""

        try:
            output_json['sentence'] = entry['sentence']
            output_json['sentence_trans'] = entry['sentence_trans']
        except Exception as e:
            output_json['sentence'] = ""
            output_json['sentence_trans'] = ""

        try:
            output_json['sentence_phrase'] = entry['sentence_phrase']
        except Exception as e:
            output_json['sentence_phrase'] = ""

        try:
            output_json['word_etyma'] = entry['word_etyma']
        except Exception as e:
            output_json['word_etyma'] = ""

        try:
            output_json['cloze_data'] = entry['cloze_data']
        except Exception as e:
            output_json['cloze_data'] = {}

        f = open("./words/" + key + ".json", "w", encoding="utf-8")
        f.write(json.dumps(output_json))
        f.close()
    except Exception as e:
        logging.error("写入文件时发生错误: " + str(e))
        fail_count += 1

logging.info("写出 json 格式文件完成.")


# 写出单词列表
list_json = json.loads("{}")
list_json['total'] = len(all_data_dict)
list_json['list'] = word_index
f = open("list.json", "w", encoding="utf-8")
f.write(json.dumps(list_json))
f.close()

logging.info("程序成功执行完成, 共计写出 " + str(len(all_data_dict)) + " 条单词数据. 发生了 " + str(fail_count) + " 个错误.")
