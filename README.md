<!--
 * @Author: hibana2077 hibana2077@gmail.com
 * @Date: 2024-03-03 14:51:05
 * @LastEditors: hibana2077 hibana2077@gmail.com
 * @LastEditTime: 2024-04-11 11:47:03
 * @FilePath: \plant_knowledge_pipepline\README.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# plant knowledge pipepline

This is a Data pipeline for plant breeding knowledge.

![Hadoop](https://img.shields.io/badge/Hadoop-000000?style=for-the-badge&logo=apache-hadoop&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

## Usage

### Prerequisites

- Docker
- Docker Compose

#### Docker

```bash
curl -sSL https://get.docker.com | sh
```

#### Docker Compose

```bash
apt update && apt install -y docker-compose
```

### Hadoop

You need to deploy a hadoop cluster first.

(recommend to use cloud service like AWS GCP, also recommend to use another computer to deploy hadoop cluster)

```bash
git clone https://github.com/hibana2077/plant_knowledge_pipepline.git
cd plant_knowledge_pipepline/hadoop
docker-compose up -d
```

### Full Pipeline

```bash
git clone https://github.com/hibana2077/plant_knowledge_pipepline.git
cd plant_knowledge_pipepline
docker-compose up -d
```

Now you can access the Neo4j browser at `http://localhost:7474` and the dashboard at `http://localhost:3000`.

If you host on a remote server, you need to change the `NEO4J_HOST` and `NEO4J_BOLT` in the `.env` file.

## License

[MIT](https://choosealicense.com/licenses/mit/)