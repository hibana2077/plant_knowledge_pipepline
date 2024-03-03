<!--
 * @Author: hibana2077 hibana2077@gmail.com
 * @Date: 2024-03-03 14:52:42
 * @LastEditors: hibana2077 hibana2077@gmail.com
 * @LastEditTime: 2024-03-03 15:28:49
 * @FilePath: \plant_knowledge_pipepline\src\TODO.md
 * @Description: TODO list
-->
# 資料管線建立與部署ToDo清單

## 一、項目準備

[preparation](./docs/preparation.md)

- [x] 確定資料來源和範圍
- [x] 定義知識圖譜的架構（實體、關係等）
- [x] 選擇技術棧和工具

## 二、開發階段

### 資料提取

- [ ] 編寫爬蟲腳本提取目標資料
- [ ] 測試並驗證爬蟲腳本的有效性

### 資料處理與轉換

- [ ] 容器化資料處理應用
- [ ] 使用NLP工具進行資料處理和結構化
- [ ] 開發資料轉換腳本，將資料轉換為知識圖譜格式

### 知識圖譜存儲

- [ ] 選擇並設置知識圖譜存儲解決方案
- [ ] 容器化知識圖譜數據庫

### Kubernetes部署

- [ ] 容器化所有應用組件
- [ ] 定義Kubernetes Deployments/StatefulSets
- [ ] 定義Kubernetes Services
- [ ] 配置PersistentVolumes和PersistentVolumeClaims
- [ ] 配置ConfigMaps和Secrets

## 三、監控與日誌

- [ ] 部署Prometheus和Grafana進行監控
- [ ] 部署ELK或EFK堆棧進行日誌管理

## 四、CI/CD管道

- [ ] 設定CI/CD流程自動化映像構建和部署
- [ ] 測試CI/CD流程

## 五、測試與優化

- [ ] 進行集成測試，確保資料管線的穩定運行
- [ ] 根據測試結果進行性能優化

## 六、文檔與維護

- [ ] 編寫項目文檔（包括架構、配置和使用指南）
- [ ] 設置維護計劃，包括定期檢查和更新
