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

## Continuidade no GitHub

O workflow `.github/workflows/nova-project-tick.yml` roda periodicamente e também pode ser executado manualmente pela aba Actions.
Ele executa um ciclo, salva estado em `.nova_project/` e faz commit dos avanços.
