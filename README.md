Eleição de Líder em Sistemas Distribuídos — Algoritmo Bully

Simulação do algoritmo Bully para eleição de coordenador em sistemas distribuídos, implementada em Python puro (sem dependências externas), usando threads reais para representar cada processo e um cenário de falha parcialmente aleatorizado a cada execução.

Trabalho final da disciplina de Sistemas Distribuídos — Engenharia de Computação, UFGD.

Autores: Lucas Thiago Dias Civardi e Luis Eduardo de Oliveira Henig
Professora: Priscila Marques Kai

Sobre o projeto

O sistema simula 12 processos (P0 a P11), onde P11 é sempre o coordenador inicial e falha logo no começo da execução. A cada execução do programa são sorteados:


Detector da falha: qual processo, entre os ativos, percebe que o coordenador caiu e inicia a eleição.
Processo extra inativo (opcional): um outro processo qualquer que também pode estar fora do ar, além do coordenador.


Isso faz com que o resultado varie a cada execução, embora o algoritmo permaneça sempre correto: o coordenador eleito é sempre o processo ativo de maior identificador.

Objetivos


Simular o algoritmo Bully em um sistema com doze processos, mostrando que o coordenador eleito é sempre o de maior ID entre os ativos, independente de quem detecta a falha ou de quais processos estão inativos.
Implementar cada processo como uma thread independente, comunicando-se apenas por troca de mensagens (ELECTION, OK, COORDINATOR).
Manter o coordenador inicial fixo em P11, para comparar com o exemplo visto em aula.
Sortear, a cada execução, quem detecta a falha e se outro processo está inativo.
Garantir que, mesmo com threads rodando em paralelo, cada eleição produza apenas um coordenador, sem mensagens duplicadas.


Como funciona o algoritmo Bully

Proposto por Garcia-Molina em 1982, o Bully elege como coordenador o processo ativo de maior identificador:


Um processo Pk que detecta a falha do coordenador envia ELECTION para todos os processos com ID maior que o seu.
Se ninguém responder, Pk vence e se torna o novo coordenador.
Se algum processo maior responder com OK, ele assume a eleição e Pk desiste, aguardando o resultado.
Quem recebe ELECTION de um processo menor responde OK e inicia sua própria eleição contra processos ainda maiores.
Esse processo se repete em cascata até restar um único vencedor, que avisa todos via COORDINATOR.


Requisitos


Python 3.14.4 (ou compatível)
Nenhuma biblioteca externa — apenas módulos padrão (threading, queue, random)


Como executar

bashpython bully_threads_LucasCivardi_EduardoHenig.py

A cada execução o cenário sorteado (detector da falha e processo extra inativo, se houver) é exibido no início do log, seguido do passo a passo das mensagens trocadas entre os processos e do resultado final, com o coordenador reconhecido por cada um deles.

Bug encontrado e corrigido

Durante os testes, identificamos uma condição de corrida: quando um mesmo processo recebia várias mensagens ELECTION quase simultâneas de remetentes diferentes, ele podia se declarar vencedor mais de uma vez, reenviando COORDINATOR repetidamente.

Correção: antes de iniciar uma nova eleição, o processo verifica se já não venceu anteriormente. Se já é coordenador, apenas confirma com OK/COORDINATOR, sem reiniciar o processo de eleição.

Resultados

ExecuçãoProcesso extra inativoDetectorVencedor1nenhumP3P102P7P5P103P10P9P94nenhumP10P10

Em todas as execuções, o vencedor foi exatamente o processo ativo de maior identificador no momento da eleição.

Vantagens e limitações

A favor: o Bully é simples de entender e sempre converge para um único coordenador, desde que as mensagens cheguem. O uso de threads reais e cenários sorteados aumentou a confiança na implementação e revelou um problema de concorrência que não apareceria em uma simulação sequencial.

Contra: no pior caso (quando quem detecta a falha é o processo de menor identificador), o número de mensagens cresce na ordem de O(n²). Além disso, a simulação roda tudo em uma única máquina; em um sistema real, cada processo estaria em uma máquina separada, com perdas de mensagem e latências mais imprevisíveis.

Referências


KAI, Priscila Marques. Eleição — Algoritmos Distribuídos — Aula 10. Material da disciplina de Sistemas Distribuídos, 2026.
BRANDÃO, José Romary. Algoritmo de Bully. YouTube, 5 jun. 2017. Disponível em: https://www.youtube.com/watch?v=K44x_VQmUs8
GUEDES, Dorgival. [FSPD] 11e: eleição de líder. YouTube, 2 nov. 2021. Disponível em: https://www.youtube.com/watch?v=W-9p_edNAnE
LEITE, Bryan. Sistemas distribuídos - Algoritmo de Bully/Eleição. YouTube, 25 mar. 2019. Disponível em: https://www.youtube.com/watch?v=SdBKJzBWtd0
