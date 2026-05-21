# Nova Project Runbook

## Objetivo

Manter ciclos de trabalho de projeto em um repositório com entrada por comandos, Actions e issues.

## Formas de entrada

1. Comando local `push`.
2. Workflow manual `nova-manual-push.yml`.
3. Issue nova ou editada pelo workflow `nova-issue-capture.yml`.
4. Ciclo periódico pelo workflow `nova-project-tick.yml`.

## Continuidade

O estado operacional fica em `.nova_project/state.json`. Saídas ficam em `.nova_project/outbox.jsonl`. Logs ficam em `.nova_project/events.log`.

## Como aproximar execução contínua

- Usar ciclos curtos e idempotentes, salvando estado a cada execução.
- Usar schedule para batimento periódico.
- Usar workflow manual para acionar quando quiser.
- Usar issue events para acionar quando houver novo pedido.
- Para ciclos longos, usar runner próprio ou ambiente externo conectado ao repositório.

## Próximos upgrades

- Capturar comentários de issues.
- Criar resumo automático nos comentários.
- Criar dashboard markdown.
- Separar papéis de pesquisa, construção, validação e publicação.
- Adicionar camada de prioridade por labels.
