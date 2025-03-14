--- Cliente da conta 8597 e containvestimento 101
INSERT INTO containvestimento (id_investimento, id_conta, perfil_invest, data_abertura)
VALUES 
(nextval('seq_conta_investimento'), 8597, 'MODERADO', '2025-01-10');

INSERT INTO fundoinvestimento (id_fundo, id_investimento, nome, data_aplicacao, valor_investido, perfil_risco, rentabilidade)
VALUES 
(nextval('seq_fundo_investimento'), 101, 'FINUPFIXO', '2025-01-10', 10000.00, 'BAIXO', 0.012);

INSERT INTO investimentos_cripto (id_cripto, id_investimento, nome, valor_investido, preco_compra, variacao_percentual, data_aplicacao, perfil_risco)
VALUES 
(nextval('seq_investimento_cripto'), 101, 'BTC', 100000, 500000, -0.0659, 2025-01-01, 'ALTO');

INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
(nextval('seq_acoes'), 101, 100, 'PETR4', 20.00, '2025-01-01', 'ALTO');

UPDATE pessoa
SET nome = 'Thiago Regueira'
WHERE nome = 'L ZiQpoGEEXGtmWAiyBWSUHGoei stqjqqozPHVVaRQngmGMRWtlNhxR';


--- Cliente da conta 10555

-- Criando um novo ID de investimento para o cliente 10555
INSERT INTO containvestimento (id_investimento, id_conta, perfil_invest, data_abertura)
VALUES 
(nextval('seq_conta_investimento'), 10555, 'ARROJADO', '2024-11-20'); -- Perfil Arrojado por ser mais novo e diversificado. Data aleatória antes de hoje

-- Inserindo dados em fundoinvestimento
INSERT INTO fundoinvestimento (id_fundo, id_investimento, nome, data_aplicacao, valor_investido, perfil_risco, rentabilidade)
VALUES 
(nextval('seq_fundo_investimento'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 'FINUPSELIC', '2024-11-25', 15000.00, 'BAIXO', 0.017);

INSERT INTO fundoinvestimento (id_fundo, id_investimento, nome, data_aplicacao, valor_investido, perfil_risco, rentabilidade)
VALUES 
(nextval('seq_fundo_investimento'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 'FINUPTESOURO', '2024-11-28', 8000.00, 'MODERADO', 0.015);

-- Inserindo dados em investimentos_cripto
-- Correção: Convertendo valores para Real
INSERT INTO investimentos_cripto (id_cripto, id_investimento, nome, valor_investido, preco_compra, data_aplicacao, perfil_risco)
VALUES 
(nextval('seq_investimento_cripto'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 'BTC', 116000, 244860, '2024-12-05', 'ALTO');
INSERT INTO investimentos_cripto (id_cripto, id_investimento, nome, valor_investido, preco_compra, data_aplicacao, perfil_risco)
VALUES 
(nextval('seq_investimento_cripto'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 'ETH', 58300, 12826, '2024-12-10', 'ALTO');

INSERT INTO investimentos_cripto (id_cripto, id_investimento, nome, valor_investido, preco_compra, data_aplicacao, perfil_risco)
VALUES 
(nextval('seq_investimento_cripto'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 'SOL', 29150, 349,8, '2024-12-15', 'ALTO');

-- Inserindo dados em acoes
INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
(nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 50, 'PETR4', 35.00, '2024-11-22', 'ALTO');
INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
(nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 100, 'VALE3', 70.00, '2024-11-25', 'ALTO');

INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
(nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 75, 'ITUB4', 28.00, '2024-11-30', 'ALTO');

INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
(nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10555), 80, 'BBDC4', 15.00, '2024-12-03', 'ALTO');

-- Cliente da conta 10556

-- Criando um novo ID de investimento para o cliente 10556
INSERT INTO containvestimento (id_investimento, id_conta, perfil_invest, data_abertura)
VALUES
    (nextval('seq_conta_investimento'), 10556, 'Moderado', '2024-11-15'); -- Perfil Moderado, data aleatória

-- Inserindo dados em fundoinvestimento
INSERT INTO fundoinvestimento (id_fundo, id_investimento, nome, data_aplicacao, valor_investido, perfil_risco, rentabilidade)
VALUES
    (nextval('seq_fundo_investimento'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 'FINUPFIXO', '2024-11-20', 12000.00, 'BAIXO', 0.012);

INSERT INTO fundoinvestimento (id_fundo, id_investimento, nome, data_aplicacao, valor_investido, perfil_risco, rentabilidade)
VALUES
    (nextval('seq_fundo_investimento'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 'CDBFINUP', '2024-11-23', 9000.00, 'BAIXO', 0.013);

-- Inserindo dados em investimentos_cripto (Valores convertidos para Real)
INSERT INTO investimentos_cripto (id_cripto, id_investimento, nome, valor_investido, preco_compra, variacao_percentual, data_aplicacao, perfil_risco)
VALUES
    (nextval('seq_investimento_cripto'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 'ETH', 87450, 13409, 0.04, '2024-11-27', 'ALTO');

INSERT INTO investimentos_cripto (id_cripto, id_investimento, nome, valor_investido, preco_compra, variacao_percentual, data_aplicacao, perfil_risco)
VALUES
    (nextval('seq_investimento_cripto'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 'USDT', 46640, 5,83, 0.00, '2024-12-02', 'ALTO');

INSERT INTO investimentos_cripto (id_cripto, id_investimento, nome, valor_investido, preco_compra, variacao_percentual, data_aplicacao, perfil_risco)
VALUES
    (nextval('seq_investimento_cripto'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 'ADA', 34980, 233,2, -0.02, '2024-12-07', 'ALTO');

-- Inserindo dados em acoes
INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
    (nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 60, 'ITUB4', 29.00, '2024-11-25', 'ALTO');

INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
    (nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 90, 'BBAS3', 50.00, '2024-11-30', 'ALTO');

INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
    (nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 45, 'VALE3', 72.00, '2024-12-05', 'ALTO');

INSERT INTO acoes (id_acoes, id_investimento, quantidade, nome, preco_inicial, data_aplicacao, perfil_risco)
VALUES
    (nextval('seq_acoes'), (SELECT MAX(id_investimento) FROM containvestimento WHERE id_conta = 10556), 70, 'ABEV3', 14.50, '2024-12-10', 'ALTO');
