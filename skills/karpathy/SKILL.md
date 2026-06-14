---
name: karpathy
description: Metodologia de engenharia LLM/neural networks estilo Andrej Karpathy - simplicidade radical, from-scratch understanding, incremental development, "teeth over education"
category: mlops
tags: [karpathy, neural-networks, llm-engineering, minimalism, first-principles]
---

# Karpathy Methodology Skill

## Princípios Fundamentais

### 1. **Simplicidade Radical** (nanoGPT philosophy)
- Código mínimo, legível, hackeável
- Zero dependências desnecessárias
- `train.py` < 300 linhas para GPT completo
- Evita frameworks pesados quando possível

### 2. **"Teeth over Education"** (Dentes sobre Educação)
> "Optimize for utility, not pedagogical completeness"
- Ferramentas que **resolvem problemas reais** > tutoriais perfeitos
- Código que roda em produção > código que ensina teoria
- Entrega valor imediato

### 3. **From-Scratch Understanding**
- Reimplemente do zero antes de usar biblioteca
- Entenda cada linha: forward, backward, optimizer, data loading
- `llm.c` - GPT-2 em C puro, 1 arquivo, 1000 linhas

### 4. **Incremental Development** (Recipe for Training Neural Networks)
```
1. Get data pipeline working (inputs → targets)
2. Init model, verify shapes
3. Overfit single batch (loss → 0)
4. Scale data, regularize
5. Hyperparameter search
6. Monitor: loss curves, gradient norms, activation stats
```

### 5. **Visualização Obsessiva**
- Loss curves em tempo real
- Gradient flow histograms
- Activation distributions
- Attention maps
- "Se você não consegue ver, não consegue debugar"

### 6. **Rigorous Debugging Checklist**
- [ ] Input shapes corretos?
- [ ] Targets alinhados com inputs?
- [ ] Loss vai a zero no overfit test?
- [ ] Gradients não explodem/vanish?
- [ ] Learning rate schedule sensato?
- [ ] Data leakage? (val no train)
- [ ] Reproducibility (seeds)?

## Workflow Prático

### Iniciar Novo Experimento
```bash
# 1. Data pipeline primeiro
python data.py --verify-shapes

# 2. Model skeleton
python model.py --init-check

# 3. Overfit sanity check (1 batch, 100 steps)
python train.py --overfit-test --steps 100

# 4. Se loss → 0: scale up
python train.py --full-run
```

### Token Economy (Economia de Contexto)
- **Logs estruturados** > prints verbosos
- **Checkpoints mínimos** (model + optimizer + step + rng)
- **Config em YAML/JSON** (não hardcode)
- **Single script entry point** (`train.py`)

### autoresearch — Autonomous ML Research Loop (2026)
Karpathy open-sourceou `autoresearch` (Ed.#005), 630 linhas de Python que transformam agentes de IA em cientistas autônomos de ML. O agente desenvolve código, executa experimentos em GPU, coleta métricas e itera sem supervisão humana.

**Loop básico:** `agente → código → execução → métricas → melhoria`
```python
# Conceito: loop de pesquisa autônoma (simplificado)
while True:
    experiment_code = agent.generate_experiment(metrics_history)
    results = run_on_gpu(experiment_code)
    metrics_history.append(results.metrics())
    if results.improvement > THRESHOLD:
        create_pr(results)
```

**Como usar no Hermes:** Script de automação CI/CD que acorda à noite, testa novas arquiteturas, abre PR se encontrar melhoria validada.

## Anti-Patterns (Evite)
- ❌ Frameworks "mágicos" que escondem detalhes
- ❌ Abstrações prematuras (trainer class antes de treinar)
- ❌ Hiperparâmetros copiados sem entender
- ❌ Métricas únicas (accuracy apenas)
- ❌ Treinar sem baseline (random init, majority class)

## Referências
- [Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/)
- [nanoGPT](https://github.com/karpathy/nanoGPT)
- [llm.c](https://github.com/karpathy/llm.c)
- [autoresearch](https://github.com/karpathy/autoresearch)
- [Zero to Hero Lecture Series](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ)

## Uso no Hermes
```
/karpathy <task>       # Aplica metodologia à task
/karpathy review       # Code review estilo Karpathy
/karpathy debug        # Checklist de debug
/karpathy autoresearch # Loop de pesquisa autônoma de ML
```