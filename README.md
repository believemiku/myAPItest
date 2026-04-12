# API接口测试框架

## 简介

这是一个基于Python的API接口测试框架，支持关键字驱动和数据驱动测试，适合小团队使用。框架提供了简洁的测试用例编写方式，支持多种数据源，集成Allure测试报告，并可与CI/CD集成。

## 功能特性

- **关键字驱动**：使用预定义关键字描述测试步骤，提高测试用例的可读性和可维护性
- **数据驱动**：支持从Excel、CSV、JSON、YAML等数据源读取测试数据
- **pytest集成**：使用pytest框架进行测试发现和执行
- **Allure报告**：集成Allure生成详细的测试报告
- **测试套件**：支持通过测试套件组织和管理测试用例
- **标记功能**：支持为测试用例添加标记（如冒烟测试）
- **灵活的断言**：支持状态码验证、JSON路径验证等
- **多种认证方式**：支持Bearer Token、Basic Auth、API Key等认证方式

## 目录结构

```
api-test-framework/
├── core/              # 核心引擎
├── keywords/          # 关键字库
├── data/              # 测试数据
├── tests/             # 测试用例
│   ├── test_cases/     # 单个测试用例
│   └── suites/         # 测试套件
├── utils/             # 工具函数
├── allure-results/    # Allure测试结果
├── allure-report/     # Allure测试报告
├── requirements.txt   # 依赖项
├── pytest.ini         # pytest配置文件
├── conftest.py        # pytest插件配置
└── README.md          # 说明文档
```

## 安装步骤

1. 克隆或下载本项目到本地
2. 进入项目目录：`cd api-test-framework`
3. 安装依赖：`pip install -r requirements.txt`
4. 安装Allure命令行工具（用于生成报告）：
   - 下载Allure命令行工具：https://github.com/allure-framework/allure2/releases
   - 解压并将bin目录添加到系统环境变量

## 使用方法

### 1. 编写测试用例

测试用例使用YAML格式编写，示例：

```yaml
# tests/test_cases/login_test.yaml
test_case:
  name: "用户登录测试"
  markers: ["smoke"]  # 测试标记
  steps:
    - keyword: "send_request"
      params:
        method: "POST"
        url: "https://jsonplaceholder.typicode.com/posts"
        headers:
          Content-Type: "application/json"
        json:
          title: "${title}"
          body: "${body}"
          userId: ${userId}
    - keyword: "assert_status_code"
      params:
        expected_status_code: 201
    - keyword: "assert_json_path"
      params:
        json_path: "$.title"
        expected_value: "${title}"
```

### 2. 准备测试数据

测试数据可以使用CSV格式，示例：

```csv
# data/csv/login_test_data.csv
title,body,userId
Test Title 1,Test Body 1,1
Test Title 2,Test Body 2,2
```

### 3. 创建测试套件

创建测试套件文件，组织测试用例和数据：

```yaml
# tests/suites/api_suite.yaml
test_suite:
  name: "API测试套件"
  test_cases:
    - path: "tests/test_cases/login_test.yaml"
      data: "data/csv/login_test_data.csv"
      markers: ["smoke"]  # 测试套件级别的标记
```

### 4. 运行测试

#### 运行测试套件

```bash
# 运行测试套件并生成Allure结果
python -m pytest tests/suites/api_suite.yaml -v --alluredir=allure-results

# 生成Allure报告
allure generate allure-results -o allure-report --clean
```

#### 运行带标记的测试

```bash
# 运行带有smoke标记的测试
python -m pytest -v -m smoke --alluredir=allure-results
```

#### 运行所有测试

```bash
# 运行所有测试
python -m pytest -v --alluredir=allure-results
```

### 5. 查看测试报告

#### 方法1：通过本地服务器查看

```bash
# 启动本地服务器
python -m http.server 8000

# 在浏览器中访问
# http://localhost:8000/allure-report/index.html
```

#### 方法2：直接打开HTML文件

```bash
# 直接打开生成的HTML报告
start allure-report/index.html
```

## 关键字说明

### 内置关键字

| 关键字 | 描述 | 参数 |
|-------|------|------|
| `send_request` | 发送HTTP请求 | method, url, headers, data, params, json |
| `assert_status_code` | 验证状态码 | expected_status_code |
| `assert_json_path` | 验证JSON路径值 | json_path, expected_value |
| `assert_response_time` | 验证响应时间 | max_time_ms |
| `set_variable` | 设置变量 | variable_name, value |
| `get_variable` | 获取变量 | variable_name |
| `add_header` | 添加请求头 | name, value |
| `authenticate` | 进行认证 | auth_type, credentials |

### 认证类型

- `bearer`: Bearer Token认证
- `basic`: Basic Auth认证
- `api_key`: API Key认证

## 示例

### 1. 基本测试

```yaml
test_case:
  name: "基本GET请求测试"
  steps:
    - keyword: "send_request"
      params:
        method: "GET"
        url: "https://jsonplaceholder.typicode.com/posts/1"
    - keyword: "assert_status_code"
      params:
        expected_status_code: 200
    - keyword: "assert_json_path"
      params:
        json_path: "$.id"
        expected_value: 1
```

### 2. 带认证的测试

```yaml
test_case:
  name: "带认证的测试"
  steps:
    - keyword: "authenticate"
      params:
        auth_type: "bearer"
        credentials:
          token: "your-token-here"
    - keyword: "send_request"
      params:
        method: "GET"
        url: "https://api.example.com/protected"
    - keyword: "assert_status_code"
      params:
        expected_status_code: 200
```

## CI/CD集成

### Jenkins

在Jenkins中创建一个自由风格的项目，添加构建步骤：

```bash
cd api-test-framework
pip install -r requirements.txt
python -m pytest tests/suites/api_suite.yaml -v --alluredir=allure-results
allure generate allure-results -o allure-report --clean
```

### GitLab CI

创建 `.gitlab-ci.yml` 文件：

```yaml
stages:
  - test

test:
  stage: test
  script:
    - cd api-test-framework
    - pip install -r requirements.txt
    - python -m pytest tests/suites/api_suite.yaml -v --alluredir=allure-results
    - allure generate allure-results -o allure-report --clean
  artifacts:
    paths:
      - api-test-framework/allure-report/
```

## 配置说明

### pytest.ini配置

```ini
[pytest]
pythonpath = .
testpaths = tests/suites/
markers =
    smoke: 冒烟测试用例
```

## 扩展开发

### 添加自定义关键字

在 `keywords/` 目录中创建新的关键字模块，然后在 `core/keyword.py` 中注册关键字。

### 添加新的数据源

在 `core/data.py` 中扩展 `DataManager` 类，添加对新数据源的支持。

## 注意事项

1. 测试用例文件必须使用YAML格式
2. 测试数据文件支持CSV、Excel、JSON、YAML格式
3. 变量引用使用 `${variable_name}` 格式
4. JSON路径使用 `$.path.to.value` 格式
5. 运行测试前建议清理 `allure-results`、`allure-report` 和 `.pytest_cache` 目录

## 故障排除

### 常见问题

1. **变量替换不生效**：检查变量名是否正确，确保测试数据中包含该变量
2. **JSON路径验证失败**：检查JSON路径是否正确，确保响应中包含该路径
3. **认证失败**：检查认证信息是否正确，确保认证类型与参数匹配
4. **Allure报告打开全是loading**：使用本地服务器打开报告，避免CORS限制

### 日志

日志文件可用于排查测试执行过程中的问题。

## 许可证

本项目采用 MIT 许可证。
