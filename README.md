# sing-box-ruleset

个人自定义 sing-box 规则集（rule-set），供远程引用。

> **命名约定**：本仓库文件一律以 **`my-`** 前缀标识，表示「我自己使用的」规则集，
> 与 `apple`、`cn`、`adblock` 这类**公共规则集**在命名上明确区分。

## 两个规则集

| 文件 | 内容 | 在配置里绑定到 |
|---|---|---|
| `my-direct.json` / `my-direct.srs` | 需要**强制直连**的域名 | `DIRECT` |
| `my-proxy.json` / `my-proxy.srs` | 需要**强制走代理**的域名 | 主出口组（如「节点选择」/「基础出站」） |

规则集本身**只描述"哪些域名"**；走哪个出口，由引用它的路由规则决定。
因此同一对规则集可被多条线路共用，各自绑定不同出口。

## 支持的过滤类型

每个规则集内部可混用三种域名条件：

| Clash 写法 | sing-box 字段 | 语义 |
|---|---|---|
| `DOMAIN` | `domain` | **精确**匹配整个域名，不含子域 |
| `DOMAIN-SUFFIX` | `domain_suffix` | 匹配该域名**及其全部子域**（含裸域本身） |
| `DOMAIN-KEYWORD` | `domain_keyword` | 域名中包含该关键词即匹配 |

**匹配逻辑**：同一条规则内，域名字段之间是 **OR**（命中任一即匹配）；
多条规则之间也是 **OR**。AND 只发生在字段组之间：
`(域名组) && (端口组) && (源端口组) && 其它字段`。

## 怎么写

打开 `my-direct.json` / `my-proxy.json`，往三个数组里填域名即可：

```json
{
  "version": 1,
  "rules": [
    {
      "domain": ["exact.example.com"],
      "domain_suffix": ["example.com", "another.net"],
      "domain_keyword": ["cdn-cgi"]
    }
  ]
}
```

- 三个字段**可以同时存在**，也可只写其中一个；用不到的留空数组 `[]` 即可。
- 想加多组规则，就往 `rules` 数组里**再加一个对象**。

### 边界提示（都是实测结论）

- `domain_suffix: ["example.com"]` 会命中 `example.com` **本身**及其所有子域，
  但**不会**误伤 `notexample.com`、`xexample.com`、`example.com.evil.net`。
- 若只想匹配**子域、不含裸域**，用带前导点的写法：`domain_suffix: [".example.com"]`。
- 域名匹配**大小写不敏感**，但**尾点不匹配**（`example.com.` 不会被 `domain` 命中）。
- 规则集内**不要**写 `rule_set`、`port` 等非域名字段 —— 它们与域名字段是 AND，会收紧匹配。

## 文件格式

- `*.json` — source 格式，可读、可直接编辑（**维护对象**）
- `*.srs` — binary 格式，由 `*.json` 编译而来（**客户端拉取对象**）

sing-box 声明 rule-set 时 `format` 字段可省略 —— 内核按**文件扩展名**自动判定：
`.json` → `source`，`.srs` → `binary`。

## 在配置里怎么声明

`tag` 同样用 **`my-`** 前缀，与公共规则集的 tag（`apple`、`cn`、`adblock` …）区分开：

```json
"route": {
  "rule_set": [
    {
      "type": "remote",
      "tag": "my-direct",
      "url": "https://cdn.jsdelivr.net/gh/Hotzenplotz-S/sing-box-ruleset@main/my-direct.srs"
    },
    {
      "type": "remote",
      "tag": "my-proxy",
      "url": "https://cdn.jsdelivr.net/gh/Hotzenplotz-S/sing-box-ruleset@main/my-proxy.srs"
    }
  ],
  "rules": [
    { "rule_set": ["my-direct"], "outbound": "DIRECT" },
    { "rule_set": ["my-proxy"], "outbound": "🚀 基础出站" }
  ]
}
```

> ⚠️ 远程规则集下载**必须显式配置 `http_client`**。
> sing-box 1.14 起，不配置时会告警「implicit default HTTP client … is deprecated
> and will be removed in sing-box 1.16.0」；`download_detour` 字段已弃用。

## 远程地址

```
https://cdn.jsdelivr.net/gh/Hotzenplotz-S/sing-box-ruleset@main/my-direct.srs
https://cdn.jsdelivr.net/gh/Hotzenplotz-S/sing-box-ruleset@main/my-proxy.srs
```

source 格式（体积略大，便于排查）：

```
https://cdn.jsdelivr.net/gh/Hotzenplotz-S/sing-box-ruleset@main/my-direct.json
https://cdn.jsdelivr.net/gh/Hotzenplotz-S/sing-box-ruleset@main/my-proxy.json
```

> jsDelivr 会缓存 `@main` 的内容，改动**不会立即生效**。
> 需要即时生效时，把 `@main` 换成具体 commit hash。

## 维护流程

1. 编辑 `my-direct.json` / `my-proxy.json`
2. 重新编译：`python build.py`（详见脚本内说明）
3. 提交推送

> ⚠️ 修改 `*.json` 后**必须**重新编译 `*.srs`，否则客户端拉到的仍是旧规则。
