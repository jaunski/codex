# Nova Project Quickstart

## Enviar uma tarefa

```bash
python nova_project/task_engine.py push --id tarefa-1 --source chat --title "Projeto teste" --text "criar projeto com planejamento execução validação e publicação"
```

## Rodar um ciclo

```bash
python nova_project/task_engine.py tick
```

## Ver estado

```bash
python nova_project/task_engine.py status
```

## GitHub Actions

- `nova-project-tick.yml` roda a cada 30 minutos e também manualmente.
- `nova-manual-push.yml` permite inserir tarefa pela aba Actions.
- `nova-issue-capture.yml` captura issues abertas ou editadas e executa um ciclo.

## Continuidade

O estado fica em `.nova_project/` e cada execução tenta salvar o avanço por commit.
