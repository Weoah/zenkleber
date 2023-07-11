# Zendesk Slack Integration Bot

O projeto de integração visa facilitar a visualização e o acompanhamento dos tempos de respostas entre a plataforma Zendesk, um sistema de suporte ao cliente, e o Slack, uma plataforma de comunicação em equipe.

## Índice

- [Visão Geral](#visão-geral)
- [Funcionamento](#funcionamento)
- [Futuramente](#futuramente)

## Visão Geral

Programado com a linguagem Python, seu funcionamento de forma simplificada ocorre através de requisições HTTP de um programa que roda a todo momento em uma máquina.
O bot atua como intermediário, permitindo que os usuários acessem e sejam notificados das informações do Zendesk diretamente do Slack.

## Funcionamento

Configuração inicial: O bot é configurado e autenticado nas respectivas contas do Zendesk e do Slack. As permissões adequadas são concedidas para acessar os dados e interagir com as APIs das duas plataformas.

Visualização de solicitações: Os usuários podem visualizar as solicitações existentes no Zendesk diretamente no Slack. Informações como o status atual, o responsável e a data de atualização são exibidas.

Notificações em tempo real: O bot envia notificações automáticas para o Slack sempre que houver uma atualização nas solicitações de suporte. Isso mantém todos os membros da equipe informados sobre as mudanças e ajuda a garantir uma comunicação eficiente.

Sincronização bidirecional: As atualizações feitas no Zendesk, como alterações de status de tickets ou respostas de agentes, são refletidas em tempo real no Slack. Isso garante que as informações estejam sempre atualizadas e sincronizadas em ambas as plataformas.

Em resumo, o bot de integração Zendesk Slack permite que os usuários acessem e gerenciem as informações do Zendesk diretamente no Slack, simplificando o fluxo de trabalho e melhorando a comunicação e a colaboração da equipe de suporte ao cliente.

## Futuramente

Integração com fluxos de trabalho existentes: O bot pode ser personalizado para se adequar aos fluxos de trabalho da equipe. Isso pode incluir a criação de comandos personalizados para automatizar tarefas, a integração com outros aplicativos ou a implementação de lógica específica para atender às necessidades da equipe.

Consulta de informações: Os usuários podem fazer consultas sobre informações específicas do Zendesk no Slack. Por exemplo, eles podem buscar o histórico de tickets de um usuário, verificar as estatísticas de suporte ou obter detalhes sobre um ticket específico.
