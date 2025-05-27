# Archive

定期导出 wiki 数据方便一些不需要实时数据的场景，顺便希望减少一些爬虫。

导出的数据为主键和原始wiki内容，即用户在/subject/1/edit或类似页面填写的原始内容。

会导出的数据包括：

- 条目（Subject）：
  
  | **Key**           | **含义**                                                                 |
  |-------------------|--------------------------------------------------------------------------|
  | `id`              | 条目 ID                                                                  |
  | `type`            | 作品类型，1表示漫画，2表示动画，3表示音乐，4表示游戏，6表示三次元             |
  | `name`            | 条目名                                                                   |
  | `name_cn`         | 条目简体中文名                                                            |
  | `infobox`         | 条目原始 **wiki** 字符串                                                   |
  | `platform`        | 条目平台，即剧场版/TV/Anime等等                                            |
  | `summary`         | 条目简介                                                                  |
  | `nsfw`            | 是否为NSFW（Not Safe For Work，是否含有成人内容）                           |
  | `date`            | 发行日期                                                                  |
  | `favorite`        | 收藏状态（想看、看过、在看、搁置、抛弃）                                     |
  | `series`          | 是否为系列作品（单行本等）                                                  |
  | `tags`            | 标签（部分）                                                              |
  | `score`           | 评分                                                                     |
  | `score_details`   | 评分细节，包含各个评分级别的分布                                            |
  | `rank`            | 类别内排名                                                                |
  | `meta_tags`       | 公共标签（由维基人管理）                                                   |

每周三凌晨五点(GMT+8)更新。

导出的数据可以在 [releases](https://github.com/bangumi/Archive/releases/tag/archive) 下载

relation, platform, staff 等常量对应关系的 yaml 文件见 [`bangumi/common`](https://github.com/bangumi/common)。

**wiki** 原始字符串的语法与解析方式，可参照 [`bangumi/wiki-parser`](https://github.com/bangumi/wiki-parser) [`wiki-parser-py`](https://github.com/bangumi/wiki-parser-py) 与 [`bangumi/wiki-syntax-spec`](https://github.com/bangumi/wiki-syntax-spec) 。

## 获取最新的导出文件地址

请获取并解析 [./aux/latest.json](./aux/latest.json) 文件，该文件会在新数据上传之后更新。


