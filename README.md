# Geter twitters with python

Autor: Péterson Silva de Jesus

Disciplina: Banco de Dados I

Curso: Ciência da Computação - IFG Anápolis.

O projeto foi construido em Python 3.

Para se executar o arquivo:
	Crie o banco de dados na sua máquina, edite o arquivo na linha 167, com as configurações da base de dados; 
	Coloque suas credencias (chaves publica e privada) do Twitter na linha 157 à 160;
	Salve o arquivo;
	Digite no terminal "python get_twitters.py";
	Assim o arquivo pegará automaticamente twitters até que você, usuário pare o programa.

O programa realiza 429 requisições e cada uma cerca de 100 twitters. Porém o twitter só deixa essa quantidade de requisições, ao chegar no limite. O twitter coloca um time de 15 minutos para poder realizar novas requisições. O programa irá esperar esses 15 minutos mostrando uma mensagem de "waiting a moment" 3 vezes na tela. Após isso, irá realizar novas requisições até o momento que o usuário decidir para-lo.
