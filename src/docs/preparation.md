<!--
 * @Author: hibana2077 hibana2077@gmail.com
 * @Date: 2024-03-03 14:55:41
 * @LastEditors: hibana2077 hibana2077@gmail.com
 * @LastEditTime: 2024-03-03 15:28:32
 * @FilePath: \plant_knowledge_pipepline\src\docs\preparation.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# 項目準備

## 資料來源和範圍

- [Frontiers in Agronomy](https://www.frontiersin.org/journals/agronomy/articles)

## 知識圖譜架構

### 一、農業知識庫架構設計

農業知識庫旨在收集、整理和利用有關農業的知識和資訊。考慮以下元素：

#### 實體（Entities）

- **作物**：名稱、種類、生長周期、種植條件
- **病蟲害**：名稱、描述、防治方法
- **農業技術**：名稱、類型、應用範圍、效果
- **農業政策**：名稱、描述、適用地區

#### 關係（Relations）

- **作物受影響於病蟲害**
- **作物適用於農業技術**
- **農業政策影響作物種植**

### 二、論文知識庫架構設計

論文知識庫旨在整理和關聯科研論文的資訊，促進學術交流和知識傳播。考慮以下元素：

#### 實體（Entities）

- **論文**：標題、摘要、關鍵詞、作者、發表日期、DOI
- **研究主題**：名稱、描述
- **作者**：名字、所屬機構、研究領域

#### 關係（Relations）

- **論文探討研究主題**
- **作者撰寫論文**
- **論文引用論文**

## 技術棧和工具

- 資料提取：Python, BeautifulSoup
- 資料處理：Python, NLP工具
- 資料轉換：Python, Py2neo, RDFLib (Python)
- 資料存儲：Neo4j, Hadoop
- 知識圖譜存儲：Neo4j
- 容器化：Docker, Kubernetes
- 監控與日誌：Prometheus, Grafana, ELK/EFK
- CI/CD管道：Jenkins, GitLab CI
