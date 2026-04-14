# document-intelligence-minio-pipeline

Este projeto mostra como estruturar um pipeline de **document intelligence** com **MinIO** como camada de armazenamento orientada a objetos. A ideia central e simples: documentos entram em uma camada `raw`, passam por uma etapa de enrichments leves, e saem em uma camada `curated` pronta para consumo por busca, analytics, OCR posterior, agentes ou RAG.

O valor do projeto nao esta em um OCR sofisticado. O valor esta em mostrar uma arquitetura documental limpa, reproduzivel e muito proxima do que aparece em plataformas reais de dados, MLOps e aplicações de IA baseadas em documentos.

## Explicacao rapida

Se alguem perguntar "o que esse projeto faz?", a resposta curta e:

- recebe documentos de varios tipos;
- grava os arquivos originais na camada `raw`;
- extrai metadados operacionais;
- salva esses metadados na camada `processed`;
- cria uma visao `curated` mais pronta para consumo;
- gera um artefato final de observabilidade do run.

## O que e MinIO e por que usar aqui

`MinIO` e um **object store compativel com a API S3**. Em termos práticos, ele permite trabalhar com os mesmos conceitos usados em pipelines baseados em buckets:

- `bucket`
- `object`
- `prefix`
- storage layers
- artefatos imutaveis
- separacao entre dado bruto e dado derivado

Isso e muito util porque boa parte dos pipelines modernos de documentos, dados e ML depende exatamente dessa logica. O MinIO permite praticar esse desenho localmente, sem depender obrigatoriamente da AWS.

## Problema que o projeto resolve

Em muitos cenarios documentais, o problema nao e so armazenar um arquivo. O problema real e:

- preservar o documento original;
- enriquecer o dado sem sobrescrever a origem;
- manter lineage entre o arquivo de entrada e o artefato derivado;
- disponibilizar uma camada pronta para uso por sistemas consumidores.

Esse projeto endereca isso com uma estrutura simples e explicita de camadas.

## Arquitetura

```mermaid
flowchart LR
    A["Incoming documents"] --> B["raw bucket"]
    B --> C["Metadata extraction"]
    C --> D["processed bucket"]
    D --> E["Curated document view"]
    E --> F["curated bucket"]
    F --> G["Pipeline report"]
```

## Fluxo do pipeline

1. O corpus de exemplo e gerado localmente com documentos como contrato, invoice, maintenance report, policy e checklist.
2. Cada documento e gravado como objeto bruto na camada `raw`.
3. O pipeline extrai sinais simples:
   - `character_count`
   - `word_count`
   - `contains_numeric_signal`
   - `summary`
4. Esses sinais sao persistidos na camada `processed`.
5. Depois disso, o pipeline cria uma classificacao documental mais pronta para consumo:
   - `legal_operational_document`
   - `finance_document`
   - `maintenance_signal_document`
   - `supply_chain_document`
   - `governance_document`
   - `field_readiness_document`
6. O resultado final e gravado na camada `curated`.
7. Um relatorio consolidado fecha o run com contagens e indicadores operacionais.

## Estrutura do repositorio

- [main.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/main.py)  
  Entry point local do pipeline.

- [app.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/app.py)  
  API simples para acionar o run.

- [src/sample_data.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/src/sample_data.py)  
  Gera o corpus documental local e a referencia do runtime.

- [src/storage.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/src/storage.py)  
  Resolve o runtime entre `MinIO` real e fallback local por filesystem.

- [src/pipeline.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/src/pipeline.py)  
  Implementa a escrita nas camadas `raw`, `processed` e `curated`, alem do relatorio final.

- [tests/test_project.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/tests/test_project.py)  
  Garante o contrato minimo do pipeline.

## Contrato das camadas

### `raw`
Representa a entrada imutavel do pipeline.

O que fica aqui:
- conteudo original do documento;
- nome do arquivo original;
- sem enriquecimentos destrutivos.

Objetivo:
- preservar a origem;
- permitir reprocessamento;
- manter auditabilidade.

### `processed`
Representa a camada de trabalho enriquecida.

O que fica aqui:
- metadados derivados;
- sinais operacionais simples;
- informacao suficiente para indexacao ou analise posterior.

Objetivo:
- separar dado derivado do dado fonte;
- evitar recalculo desnecessario;
- criar uma camada reutilizavel para outros pipelines.

### `curated`
Representa a camada pronta para consumo por aplicacoes.

O que fica aqui:
- classificacao documental;
- resumo operacional;
- estrutura mais legivel para analytics, busca e sistemas consumidores.

Objetivo:
- aproximar o dado do uso final;
- reduzir acoplamento com a logica de preprocessamento;
- facilitar integracao com agentes, dashboards e mecanismos de busca.

## Runtime modes

O projeto funciona em dois modos.

### 1. `minio_s3_api`
Ativado quando estas variaveis estao disponiveis:

- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- opcional `MINIO_SECURE`

Nesse modo, o pipeline grava objetos em um servidor MinIO real, mantendo uma experiencia muito proxima de workloads baseados em `S3`.

### 2. `local_filesystem_fallback`
Se o runtime MinIO nao estiver configurado, o projeto usa uma simulacao local em:

- `data/object_store/raw`
- `data/object_store/processed`
- `data/object_store/curated`

Esse fallback existe para garantir:

- reproducibilidade;
- execucao local sem dependencia externa;
- testes automatizados estaveis;
- demonstracao de arquitetura mesmo sem servidor ativo.

## Como executar

```bash
python3 main.py
```

Para subir a API:

```bash
uvicorn app:app --reload
```

## Endpoints

- `GET /health`
- `POST /run`

## Resultado atual

- `dataset_source = document_intelligence_minio_local_sample`
- `runtime_mode = local_filesystem_fallback`
- `document_count = 6`
- `raw_object_count = 6`
- `processed_object_count = 6`
- `curated_object_count = 6`
- `maintenance_signal_documents = 1`

## Artefatos gerados

- relatorio consolidado:
  [document_intelligence_minio_report.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/data/processed/document_intelligence_minio_report.json)
- camada `curated`:
  [curated_documents.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/document-intelligence-minio-pipeline/artifacts/curated_documents.json)

## Leitura tecnica

Tecnicamente, o projeto demonstra alguns principios importantes:

- **immutability by layer**  
  o documento fonte nao e sobrescrito por metadados derivados;

- **lineage simples e explicito**  
  o mesmo `document_id` atravessa as camadas;

- **storage-first design**  
  a persistencia nao e um detalhe do pipeline; ela e parte da arquitetura;

- **consumer-oriented curation**  
  a camada `curated` ja pensa no uso final por sistemas consumidores.

## Como defender esse projeto em entrevista

Uma boa forma de explicar esse repositório e:

"Eu quis mostrar como usar MinIO como object storage compativel com S3 para organizar um pipeline documental por camadas. O documento original vai para `raw`, os metadados derivados vao para `processed`, e a visao mais pronta para consumo vai para `curated`. Isso ajuda com reprocessamento, governanca, lineage e integracao com busca, RAG ou analytics."

## Evolucoes naturais

Esse projeto pode evoluir facilmente para:

- OCR com `Textract`, `Tesseract` ou parser de PDF;
- indexacao em Elasticsearch ou vector store;
- pipeline de embeddings para RAG;
- versionamento de artefatos de ML;
- eventos de bucket para acionar processamento automatico;
- integracao com Airflow, Metaflow ou workflows serverless.

## English

This project shows how to structure a **document intelligence pipeline** using **MinIO** as the object-storage layer. The main idea is straightforward: documents land in a `raw` layer, go through lightweight enrichments, and leave the pipeline in a `curated` layer ready for search, analytics, OCR follow-up, agents, or RAG.

The value of this repository is not advanced OCR. Its value is the architecture: a clean, reproducible, storage-first design that mirrors real-world document platforms.

### What MinIO means here

`MinIO` is `S3-compatible object storage`. That matters because many modern data and ML systems rely on buckets, immutable objects, prefixes, and layered storage. This project uses MinIO to practice that architecture in a portable way.

### Pipeline flow

1. A local document corpus is generated.
2. Original content is stored in the `raw` bucket.
3. Lightweight metadata is extracted.
4. Derived metadata is stored in the `processed` bucket.
5. A consumer-facing classification layer is written to `curated`.
6. A pipeline report closes the run.

### Storage contract

- `raw`: immutable source layer
- `processed`: derived metadata layer
- `curated`: consumer-ready layer

### Runtime behavior

The repository supports:

- `minio_s3_api`: writes to a real MinIO server when credentials are configured
- `local_filesystem_fallback`: deterministic local simulation when MinIO is not available

### Current result

- `dataset_source = document_intelligence_minio_local_sample`
- `runtime_mode = local_filesystem_fallback`
- `document_count = 6`
- `raw_object_count = 6`
- `processed_object_count = 6`
- `curated_object_count = 6`
- `maintenance_signal_documents = 1`

### Why this project is useful

This repository is a strong base for:

- document AI pipelines
- OCR artifact storage
- RAG document repositories
- compliance-oriented document retention
- storage-first MLOps workflows
