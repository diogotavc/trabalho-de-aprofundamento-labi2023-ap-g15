Nome - Nmec - Contribuição

<a href="mailto:diogo.tav.carvalho@ua.pt"><strong>Diogo Tavares Carvalho</strong> (113221)</a> [65%]

<a href="mailto:goncalobmartins@ua.pt"><strong>Gonçalo Biscaia Martins</strong> (112678)</a> [35%]

[Link para o repositório](https://github.com/detiuaveiro/trabalho-de-aprofundamento-labi2023-ap-g15) - [Link para o branch antigo](https://github.com/detiuaveiro/trabalho-de-aprofundamento-labi2023-ap-g15/tree/archive)

To-do

1. ~~Opção para ativar e desativar logs~~

2. ~~Implementar testes~~

Observações finais:

- Relativo ao ponto número 1 da lista acima, são mencionados 'logs' (ou seja, as mensagens [INFO], [DEBUG], etc.) pois, devido à falta de tempo (parcialmente por causa da mudança de branch), não foram implementados de forma correta, idealmente com opção para ativar e desativar as mesmas através de uma flag (i.e. --logs ou -l).

- Já relativo ao ponto número 2, foi decidido que não valeria a pena implementar os testes automáticos, visto que o código foi testado exaustivamente durante o desenvolvimento. Caso este projeto tivesse como objetivo continuar a ser trabalhado e melhorado, faria sentido implementá-los, de forma a facilitar a manutenção, a aumentar a rapidez da testagem, e a eliminar erros humanos durante os testes. Contudo, com o recomeço no desenvolvimento (o código antigo encontra-se no [branch 'archive'](https://github.com/detiuaveiro/trabalho-de-aprofundamento-labi2023-ap-g15/tree/archive)), a testagem foi muito mais rigorosa (tendo sido tudo testado da melhor maneira possível, com a exceção de falhas na conexão, visto que só foi possível executar o cliente e o servidor no localhost diretamente), e testes automáticos não se justificaram, devido à dimensão do código. Foram, no entanto, implementados testes básicos, contudo não servem para _(praticamente)_ nada.

- Os pequenos tempos de espera (0.25s), durante o start_action e entre inputs, é para prevenir que o servidor receba demasiados requests e que não os consiga processar a tempo (especialmente quando a encriptação se encontra ativa). Não é a melhor solução, mas é uma forma de resolver, quase por completo, o problema.