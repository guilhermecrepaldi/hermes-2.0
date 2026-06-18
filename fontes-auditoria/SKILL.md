---
name: fontes-auditoria-software
description: "Guia de softwares de auditoria open source e gratuitos — organizado por categoria: GRC, rede/infra, segurança/licença, compliance, monitoramento. Inclui Lynis, Open-AudIT, Eramba, Wazuh, OpenVAS, ScanCode, FOSSology, Grafana + comparativos."
category: software-development
tags: [auditoria, compliance, seguranca, grc, rede, licenca, open-source]
---

# Softwares de Auditoria — Fonte de Estudo

## Mapa de Categorias

| Categoria | O que audita | Ferramentas Principais |
|-----------|-------------|----------------------|
| **GRC** (Governança, Risco e Compliance) | Políticas, riscos, controles internos | Eramba |
| **Rede e Infraestrutura** | Inventário de rede, configurações, mudanças | Open-AudIT, Opmantek, Nmap |
| **Segurança do Sistema** | Hardening, vulnerabilidades, conformidade CIS | Lynis, OpenVAS, Wazuh |
| **Licença e Código** | Licenças OSS, dependências, SBOM | ScanCode, FOSSology, ORT, Snyk |
| **Monitoramento e Logs** | Logs, eventos, SIEM | Wazuh, Grafana Loki, OpenSearch |
| **Testes de Segurança (DAST/SAST)** | Vulnerabilidades em apps web | OWASP ZAP, Nikto, SonarQube |

---

## 1. GRC — Governança, Risco e Compliance

### Eramba
- **Site**: https://www.eramba.org
- **Modelo**: Open Source (Community Edition gratuita) + Enterprise paga
- **Descrição**: Principal GRC open source do mercado. Gestão de riscos, compliance, políticas, auditorias internas.
- **Features**:
  - Asset management com classificação de risco
  - Gestão de políticas e procedimentos
  - Mapeamento de controles (NIST, ISO 27001, SOC 2, PCI DSS)
  - Workflow de auditoria (planos, evidências, não-conformidades)
  - Dashboard e relatórios exportáveis
  - Cadastro de fornecedores e due diligence
- **Stack**: PHP (CakePHP), MySQL/MariaDB
- **GitHub**: https://github.com/eramba/eramba_community

---

## 2. Rede e Infraestrutura

### Open-AudIT
- **Site**: https://www.open-audit.org
- **Modelo**: Open Source (Community) + Enterprise paga
- **Descrição**: Inventário completo de rede — hardware, software, configurações, mudanças.
- **Features**:
  - Descoberta automática de dispositivos (Windows, Linux, macOS, network gear)
  - Inventário de hardware e software
  - Auditoria de configurações
  - Alertas de mudanças
  - Relatórios de compliance
  - Suporte a Windows e Linux
- **Stack**: PHP, MySQL/MariaDB, CodeIgniter
- **GitHub**: https://github.com/Opmantek/open-audit

### Opmantek
- **Site**: https://www.opmantek.com
- **Modelo**: Open Source + Enterprise
- **Descrição**: Plataforma de gerenciamento e auditoria de TI. Usada por 115K+ organizações.
- **Features**: Monitoramento de rede, auditoria de configurações, automação de ITIL, alertas
- **Ferramentas do ecossistema**: Open-AudIT (auditoria), Opmantek NMIS (monitoramento)

### Nmap
- **Site**: https://nmap.org
- **Modelo**: **100% Open Source**
- **Descrição**: Scanner de rede mais famoso do mundo. Descobre hosts, portas, serviços, sistemas operacionais.
- **Uso típico em auditoria**: Mapear superfície de ataque, identificar serviços não-autorizados, inventário de rede

---

## 3. Segurança do Sistema e Hardening

### Lynis
- **Site**: https://github.com/CISOfy/lynis
- **Modelo**: Open Source (Community) + Enterprise
- **Descrição**: Ferramenta de auditoria de segurança para sistemas Unix/Linux, macOS, BSD. Testa defesas e sugere hardening.
- **Features**:
  - 300+ testes de segurança
  - Compliance com CIS, PCI DSS, HIPAA, ISO 27001
  - Sugestões de hardening por categoria
  - Escaneia sem dependências (shell script puro)
  - Gera relatórios detalhados
  - Ideal para auditoria de conformidade de servidores
- **Comando**: `lynis audit system`
- **GitHub**: 28K+ estrelas

### OpenVAS (Greenbone)
- **Site**: https://www.greenbone.net
- **Modelo**: Open Source
- **Descrição**: Scanner de vulnerabilidades completo. Mais de 100K testes de vulnerabilidade.
- **Uso**: Escaneamento periódico de redes, identificação de CVEs, relatórios de risco
- **Stack**: Linux (Kali, Ubuntu), Docker

---

## 4. SIEM e Monitoramento de Segurança

### Wazuh
- **Site**: https://wazuh.com
- **Modelo**: **100% Open Source**
- **Descrição**: Plataforma unificada de XDR e SIEM. Monitora endpoints, cloud workloads, logs.
- **Features**:
  - Coleta e análise de logs em tempo real
  - Detecção de intrusão (IDP)
  - Auditoria de conformidade (PCI DSS, HIPAA, GDPR, NIST)
  - Escaneamento de vulnerabilidades integrado
  - Resposta a incidentes automatizada
  - Integração com OpenVAS
- **Stack**: Elasticsearch/OpenSearch, Filebeat, agentes multi-plataforma
- **GitHub**: 10K+ estrelas

---

## 5. Licença e Auditoria de Código

### ScanCode Toolkit
- **Site**: https://github.com/nexB/scancode-toolkit
- **Modelo**: **100% Open Source** (Apache 2.0)
- **Descrição**: Detecta licenças, copyrights e dependências em código fonte. Projeto da Linux Foundation.
- **Features**:
  - Detecção de licenças (SPDX)
  - Detecção de copyright
  - Análise de dependências
  - Geração de SBOM (SPDX, CycloneDX)
  - CLI e integração CI/CD
- **Uso**: `scancode --license --copyright --info ./projeto`
- **GitHub**: 6K+ estrelas

### FOSSology
- **Site**: https://www.fossology.org
- **Modelo**: **100% Open Source** (Linux Foundation)
- **Descrição**: Sistema de compliance de licenças OSS. REST API, web UI, scans em lote.
- **Features**:
  - Scanner de licenças e copyrights
  - Workflow de revisão de licenças
  - Relatórios SPDX
  - Bulk scanning
- **GitHub**: 2K+ estrelas

### OSS Review Toolkit (ORT)
- **Site**: https://github.com/oss-review-toolkit/ort
- **Modelo**: **100% Open Source** (Apache 2.0)
- **Descrição**: Pipeline automatizado de auditoria de licenças para projetos de software. Da análise à geração de relatório.
- **Features**: Análise de dependências, escaneamento de licenças, geração de relatórios de compliance, integração CI/CD
- **Mantido por**: HERE Technologies, Bosch, outros

### Snyk
- **Site**: https://snyk.io
- **Modelo**: Freemium (gratuito para projetos open source)
- **Descrição**: Segurança de código aberto e análise de dependências. Detecta vulnerabilidades + licenças.
- **Features**: SCA (Software Composition Analysis), SAST, Container scanning, IaC scanning
- **GitHub**: Integração nativa

---

## 6. Testes de Segurança (DAST/SAST)

### OWASP ZAP
- **Site**: https://www.zaproxy.org
- **Modelo**: **100% Open Source**
- **Descrição**: Scanner de segurança de aplicações web. Padrão-ouro OWASP para DAST.
- **Features**: Proxy interceptador, scanner automático, spider, fuzzing, websockets, API

### Nikto
- **Site**: https://github.com/sullo/nikto
- **Modelo**: **100% Open Source** (GPL)
- **Descrição**: Scanner de servidores web. Testa 6700+ arquivos/scripts potencialmente perigosos.
- **Uso**: `nikto -h https://exemplo.com`

### SonarQube
- **Site**: https://www.sonarsource.com/products/sonarqube/
- **Modelo**: Community Edition **Open Source** + editions pagas
- **Descrição**: Análise estática de código (SAST). Detecta bugs, vulnerabilidades, code smells, code coverage.
- **Linguagens**: 30+ (Java, Python, JS, TS, C#, Go, etc.)
- **Uso**: pipeline CI/CD, qualidade contínua

---

## 7. Infraestrutura e Redes (extra)

| Ferramenta | Tipo | Descrição |
|-----------|------|-----------|
| **Grafana Loki** | Log aggregation | Agregação de logs, consultas, alertas |
| **OpenSearch** | Search & SIEM | Fork open source do Elasticsearch |
| **Osquery** | System introspection | Consultas SQL ao SO (processos, conexões, arquivos) |
| **Falco** | Runtime security | Detecção de comportamento anômalo em containers |
| **CIS Benchmarks** | Hardening guides | Guias de configuração segura por SO/plataforma |

---

## Quick Reference — Comandos de Auditoria

```bash
# Lynis — auditoria de segurança do sistema
lynis audit system

# Nmap — descoberta de rede
nmap -sV -sC -O 192.168.1.0/24

# OpenVAS — escaneamento de vulnerabilidades (via gvm-cli)
gvm-cli --gmp-username admin scan --target "192.168.1.0/24"

# ScanCode — auditoria de licenças em código
scancode --license --copyright --info ./meu-projeto

# OWASP ZAP — scanner de app web (CLI)
zap-cli quick-scan https://minhaapp.com

# Osquery — consultar processos
osqueryi "SELECT name, pid, path FROM processes WHERE on_disk=0;"
\n# Nikto — scanner de servidor web\nnikto -h https://exemplo.com -ssl\n```\n\n---\n\n## Papers Acadêmicos — Referências para Estudo\n\n### AuditWen: An Open-Source Large Language Model for Audit\n- **Link**: https://arxiv.org/abs/2410.10873\n- **Ano**: 2024 (CCL 2024 / ACL FinNLP 2025)\n- **Autores**: Huang et al.\n- **Resumo**: Primeiro LLM open source específico para auditoria. Fine-tune do Qwen-7B com 30K instruções em 15 tarefas de auditoria. Benchmark de 5K instruções para tarefas críticas.\n- **Tarefas**: Classificação de risco, extração de evidências, sumarização de relatórios, detecção de anomalias\n- **GitHub**: https://github.com/HooRin/AuditWen\n- **Relevância**: Prova de conceito de como LLMs podem ser especializados para auditoria\n\n### Cost-Effective Resilience: A Comprehensive Survey on Open-Source Cybersecurity Tools\n- **Link**: https://ieeexplore.ieee.org/abstract/document/10772461\n- **Ano**: 2024 (IEEE)\n- **Descrição**: Survey sistemático de ferramentas open source de cibersegurança para defesa multi-camadas. Abrange ferramentas de auditoria, monitoramento, detecção e resposta.\n- **Relevância**: Mapa completo do ecossistema de ferramentas open source de segurança\n\n### Comparative Analysis of Open-Source Vulnerability Assessment Tools\n- **Link**: https://ieeexplore.ieee.org/document/10100030\n- **Ano**: 2023 (IEEE)\n- **Descrição**: Análise comparativa detalhada de ferramentas de vulnerabilidade open source. Inclui estudo de caso com Zenmap (Nmap GUI) em rede de campus universitário.\n- **Ferramentas analisadas**: Nmap/Zenmap, OpenVAS, Nessus (comparativo)\n- **Relevância**: Benchmark prático de ferramentas de escaneamento de rede\n\n### Empowering Cybersecurity with Free and Open-Source Tools — A White Paper\n- **Link**: https://hivehub.org/wp-content/uploads/2025/07/Empowering-Cybersecurity-with-Free-and-Open-Source-Tools.pdf\n- **Ano**: 2025\n- **Descrição**: Coleta curada de 50+ ferramentas open source de cibersegurança, organizadas por função, com descrições, casos de uso e guias de setup.\n- **Relevância**: Catálogo prático e extenso de ferramentas\n\n### 2026 Open Source Security and Risk Analysis Report — Black Duck\n- **Link**: https://www.blackduck.com/content/dam/black-duck/en-us/reports/rep-ossra.pdf\n- **Ano**: 2026 (baseado em auditorias Nov/2024 — Out/2025)\n- **Descrição**: Relatório anual sobre uso de OSS e riscos associados. Baseado em auditorias reais de código.\n- **Relevância**: Dados reais de mercado sobre riscos de OSS em software comercial\n\n### AI-Driven Auditing: Trends, Themes, and Future Directions\n- **Link**: https://www.sciencedirect.com/science/article/pii/S2199853125001088\n- **Ano**: 2025 (ScienceDirect)\n- **Descrição**: Revisão sistemática de 100 artigos (2015-2025) sobre IA na auditoria. ML, NLP, RPA e outros métodos.\n- **Relevância**: Estado-da-arte do uso de IA em processos de auditoria\n\n### Open Source Solutions for Vulnerability Assessment: A Survey\n- **Link**: https://ieeexplore.ieee.org/document/10251527\n- **Ano**: 2023 (IEEE)\n- **Descrição**: Survey focado em soluções open source para avaliação de vulnerabilidades, contrastando com soluções comerciais.\n- **Relevância**: Comparativo OSS vs comercial para decisão de ferramentas\n\n### Vercation: Precise Vulnerable Open-Source Software Version Identification\n- **Link**: https://ieeexplore.ieee.org/document/11129942\n- **Ano**: 2025 (IEEE)\n- **Descrição**: Método para identificar versões vulneráveis de OSS analisando code features. Essencial para auditoria de dependências.\n- **Relevância**: Técnica para auditoria precisa de versões de dependências\n\n### Audit Trails for Accountability in Large Language Models\n- **Link**: https://arxiv.org/html/2601.20727v1\n- **Ano**: 2026 (arXiv)\n- **Descrição**: Framework lifecycle para audit trails de LLMs. Arquitetura de referência com emitters, audit stores e interface de auditoria.\n- **Relevância**: Como auditar sistemas que usam LLMs — tópico emergente\n\n### Auditing LLMs: AuditLLM — A Tool for Auditing Large Language Models\n- **Link**: https://dl.acm.org/doi/abs/10.1145/3627673.3679222\n- **Ano**: 2024 (ACM)\n- **Descrição**: Ferramenta para auditar LLMs usando variações de queries para revelar inconsistências.\n- **Relevância**: Metodologia para auditoria de modelos de IA
