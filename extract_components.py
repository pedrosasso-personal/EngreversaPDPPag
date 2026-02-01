#!/usr/bin/env python3
"""
Script para extrair dados das fichas de componentes e gerar CSV consolidado.
"""

import os
import re
import json
import csv
from pathlib import Path

# Mapeamento de prefixos para tecnologias
PREFIXO_TECNOLOGIA = {
    "sboot": "Spring Boot",
    "springboot": "Spring Boot",
    "sbootlib": "Spring Boot (Library)",
    "sbatch": "Spring Batch",
    "javabatch": "Java Batch",
    "java": "Java EE",
    "ang": "Angular",
}


# Mapa de domínios com palavras-chave para classificação
DOMINIOS = {
    "01.03": {
        "nome": "Agente de Pagamentos",
        "keywords": ["assistência", "criação de pagamentos", "múltiplas modalidades", "instrução estruturada", "inteligência artificial", "assistente", "chatbot", "orientação"]
    },
    "02.01": {
        "nome": "Agendamento e Recorrência",
        "keywords": ["agendamento", "agendado", "recorrência", "recorrente", "pagamentos futuros", "débito automático", "calendário", "fila de execução", "retentativa", "schedule", "scheduled", "programado"]
    },
    "02.02": {
        "nome": "Validações de Pagamento",
        "keywords": ["validação", "validar", "conformidade", "verificação", "integridade", "pré-autorização", "consistência", "regras de negócio", "validações"]
    },
    "02.03": {
        "nome": "Transação e Processamento",
        "keywords": ["execução", "processamento", "processar", "movimentação", "liquidação", "liquidar", "contabilização", "contábil", "arranjos", "SPI", "DICT", "devolução", "estorno", "efetivação", "efetivar", "transação", "pagamento", "transferência", "ted", "tef", "pix", "boleto"]
    },
    "02.04": {
        "nome": "Instrumentos de Pagamento",
        "keywords": ["emissão", "geração", "gerar boleto", "código de barras", "linha digitável", "qr code", "qrcode", "criação de boleto", "instrumento", "cobrança"]
    },
    "02.05": {
        "nome": "Processamento de Recebimento",
        "keywords": ["recebimento", "compensação", "conciliação", "baixa", "cash-in", "cashin", "crédito recebido", "repasse"]
    },
    "03.01": {
        "nome": "Informações Corporativas",
        "keywords": ["dados mestres", "parâmetros", "instituições financeiras", "ISPB", "feriados", "municípios", "parametrização", "tabelas", "configuração", "cadastro básico"]
    },
    "04.01": {
        "nome": "Favorecidos",
        "keywords": ["beneficiários", "favorecidos", "favorecido", "destinatário", "contatos", "cadastro de favorecido"]
    },
    "04.02": {
        "nome": "Limites",
        "keywords": ["limites", "limite operacional", "valores máximos", "alçadas", "consumo de limite", "disponibilidade de limite"]
    },
    "04.03": {
        "nome": "Tarifas e Tributos",
        "keywords": ["tarifas e tributos", "IOF e ISS", "split payment tributário"]
    },
    "04.04": {
        "nome": "Comprovantes",
        "keywords": ["comprovantes", "comprovante", "segunda via", "autenticação bancária", "recibo"]
    },
    "04.05": {
        "nome": "Notificações e Relatórios",
        "keywords": ["notificações", "notificação", "SMS", "email", "push", "WhatsApp", "relatórios", "alertas", "comunicação", "envio de email"]
    },
    "04.06": {
        "nome": "DDA (Débito Direto Autorizado)",
        "keywords": ["DDA", "débito direto autorizado", "boletos eletrônicos", "Núclea", "boletodda"]
    },
    "04.07": {
        "nome": "Autorizações",
        "keywords": ["autorização", "autorizador", "aprovação", "alçadas", "poderes de assinatura", "aprovadores", "assinatura"]
    },
    "04.08": {
        "nome": "Tarifas",
        "keywords": ["tarifas", "tarifa", "tarifação", "tarifador", "cobrança de tarifa", "isenção"]
    },
    "04.09": {
        "nome": "Tributos",
        "keywords": ["tributos", "tributo", "IOF", "ISS", "DARF", "GPS", "arrecadação", "imposto", "fiscal"]
    },
    "05.01": {
        "nome": "Dados e Monitoramento",
        "keywords": ["monitoramento", "monitora", "métricas", "performance", "SLA", "dashboards", "cockpit", "observabilidade", "health check"]
    },
    "05.02": {
        "nome": "Logs e Auditoria",
        "keywords": ["logs", "log", "auditoria", "rastreabilidade", "histórico", "eventos", "registro de eventos"]
    },
    "06.01": {
        "nome": "Iniciação de Pagamentos",
        "keywords": ["Open Finance", "open banking", "iniciação", "ITP", "consentimentos", "iniciador"]
    },
    "06.02": {
        "nome": "Compartilhamento de Dados",
        "keywords": ["compartilhamento", "dados transacionais", "consentimento", "LGPD", "acesso a dados"]
    }
}

# Descrições das siglas baseadas nos nomes dos componentes
SIGLAS_DESC = {
    "CCDB-BASE": "Conta Corrente e Débitos - Base",
    "ERPT-BASE": "Enterprise Reporting - Base",
    "FLEX-CALC": "Flexibilização - Cálculos",
    "FLEX-INBV": "Flexibilização - Integração BV",
    "FLEX-ORAC": "Flexibilização - Oracle",
    "FLEX-PARC": "Flexibilização - Parcelamento",
    "GDCC-BASE": "Gestão de Conta Corrente - Base",
    "GRCB-FGOD": "GRC Bradesco - FGOD",
    "GRCB-MREC": "GRC Bradesco - Módulo Recebimento",
    "INTB-BASE": "Integração Bancária - Base",
    "INTB-ONDA": "Integração Bancária - ONDA",
    "OPEN-PCRE": "Open Finance - Portabilidade de Crédito",
    "PAGM-BASE": "Pagamentos - Base",
    "PGFT-BASE": "Pagamentos Fintech - Base",
    "RRCB-BASE": "Reconciliação e Recebimentos - Base",
    "SACA-SCCO": "Saque e Caixa - SCCO",
    "SCOB-BASE": "Sistema de Cobrança - Base",
    "SITP-BASE": "Sistema de Tarifas e Produtos - Base",
    "SPAG-BASE": "Sistema de Pagamentos - Base",
    "SPAG-FINT": "Sistema de Pagamentos - Fintech",
    "SPAG-PIXX": "Sistema de Pagamentos - PIX",
    "SPAG-SPIB": "Sistema de Pagamentos - SPIB",
    "SPBB-BASE": "SPB Bradesco - Base",
    "SPBB-ISPB": "SPB Bradesco - ISPB",
    "PROJETOS_VISUAL_BASIC": "Projetos Visual Basic"
}


def extract_description(file_path):
    """Extrai a descrição geral de uma ficha de componente."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tentar encontrar seção de Descrição Geral
        patterns = [
            r'##\s*1\.\s*Descrição Geral\s*\n+(.+?)(?=\n##|\n---|\Z)',
            r'###\s*1\.\s*Descrição Geral\s*\n+(.+?)(?=\n##|\n###|\n---|\Z)',
            r'##\s*Descrição Geral\s*\n+(.+?)(?=\n##|\n---|\Z)',
            r'###\s*Descrição Geral\s*\n+(.+?)(?=\n##|\n###|\n---|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                # Limpar e normalizar
                desc = re.sub(r'\s+', ' ', desc)
                desc = desc[:500] if len(desc) > 500 else desc
                return desc

        # Se não encontrou, pegar primeiros parágrafos após o título
        lines = content.split('\n')
        desc_lines = []
        started = False
        for line in lines:
            if line.startswith('#'):
                if started:
                    break
                started = True
                continue
            if started and line.strip():
                desc_lines.append(line.strip())
                if len(' '.join(desc_lines)) > 300:
                    break

        if desc_lines:
            desc = ' '.join(desc_lines)
            desc = re.sub(r'\s+', ' ', desc)
            return desc[:500]

        return "Descrição não encontrada"
    except Exception as e:
        return f"Erro ao ler: {str(e)}"


def extract_technology(file_path, component_name):
    """Extrai a tecnologia/linguagem de uma ficha de componente."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tentar encontrar seção de Tecnologias Utilizadas
        patterns = [
            r'###?\s*\d*\.?\s*Tecnologias Utilizadas\s*\n+(.+?)(?=\n##|\n###|\n---|\Z)',
            r'###?\s*Tecnologias\s*\n+(.+?)(?=\n##|\n###|\n---|\Z)',
        ]

        tech_section = None
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                tech_section = match.group(1).strip()
                break

        # Extrair Framework principal da seção
        if tech_section:
            # Procurar por Framework
            framework_match = re.search(r'\*\*Framework:\*\*\s*(.+?)(?:\n|$)', tech_section)
            if framework_match:
                framework = framework_match.group(1).strip()
                # Limpar e simplificar
                framework = re.sub(r'\s+\d+\.[\dx]+.*', '', framework)  # Remove versões
                framework = framework.split(',')[0].strip()  # Pega só o primeiro se tiver vírgula
                return framework

            # Procurar por Linguagem
            lang_match = re.search(r'\*\*Linguagem:\*\*\s*(.+?)(?:\n|$)', tech_section)
            if lang_match:
                return lang_match.group(1).strip().split(',')[0].strip()

        # Fallback: usar prefixo do nome do componente
        name_lower = component_name.lower()
        for prefixo, tech in PREFIXO_TECNOLOGIA.items():
            if name_lower.startswith(prefixo + "-") or name_lower.startswith(prefixo + "_"):
                return tech

        # Fallback final baseado em padrões no nome
        if 'angular' in name_lower or name_lower.startswith('ang-'):
            return "Angular"
        if 'spring' in name_lower:
            return "Spring Boot"
        if 'batch' in name_lower:
            return "Java Batch"

        return "Java"  # Default

    except Exception as e:
        return "Desconhecido"


def extract_function(file_path, component_name):
    """Extrai uma descrição funcional curta e direta do componente."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extrair descrição geral
        desc_match = re.search(
            r'###?\s*1\.?\s*Descrição Geral\s*\n+(.+?)(?=\n##|\n###|\n---|\Z)',
            content, re.DOTALL | re.IGNORECASE
        )

        if not desc_match:
            return infer_function_from_name(component_name)

        desc = desc_match.group(1).strip()

        # Pegar as duas primeiras sentenças
        sentences = re.split(r'(?<=[.!?])\s+', desc)
        raw_text = ' '.join(sentences[:2]) if sentences else desc

        # 2. Limpar termos técnicos de forma agressiva
        cleanups = [
            # Remover nomes do sistema entre aspas ou negrito
            (r'^O sistema "[^"]+" é ', ''),
            (r'^O sistema \*\*[^*]+\*\* é ', ''),
            (r'^O \*\*[^*]+\*\* é ', ''),
            (r'O sistema "[^"]+" é ', ''),

            # Remover frases técnicas introdutórias
            (r'^O sistema é um[a]? ', ''),
            (r'^Este sistema é ', ''),
            (r'^Trata-se de um[a]? ', ''),
            (r'^Sistema de ', ''),
            (r'^Projeto ', ''),
            (r'^Componente ', ''),
            (r'^Serviço ', ''),
            (r'^Microserviço ', ''),
            (r'^Aplicação ', ''),
            (r'^Aplicativo ', ''),
            (r'^Um processador ', 'Processador de '),
            (r'^Processamento processamento', 'Processamento'),

            # Remover descrições técnicas
            (r'desenvolvid[oa] em [^,\.]+[,\.]?\s*', ''),
            (r'utilizando o? ?framework [^,\.]+[,\.]?\s*', ''),
            (r'em arquitetura de microserviços[^,\.]*[,\.]?\s*', ''),
            (r'que utiliza o framework [^,\.]+[,\.]?\s*', ''),
            (r'Ele utiliza o framework [^,\.]+[,\.]?\s*', ''),
            (r'para gerenciamento de dependências[^,\.]*[,\.]?\s*', ''),
            (r'e construção[,\.]?\s*', ''),
            (r'para gerenciar recursos e o\s*$', ''),

            # Remover tecnologias e frameworks
            (r'\bSpring Boot[^,\.]*', ''),
            (r'\bSpring Batch[^,\.]*', ''),
            (r'\bSpring\b', ''),
            (r'\bJava EE[^,\.]*', ''),
            (r'\bAngular[^,\.]*', ''),
            (r'\bMaven[^,\.]*', ''),
            (r'\bJava\b(?!\s+que)', ''),  # Remove Java sozinho mas não "Java que"
            (r'\(\)', ''),  # Remove parênteses vazios

            # Remover termos vagos
            (r'\bstateless\b', ''),
            (r'\bbatch\b', ''),
            (r'\bAPIs? REST\b', ''),

            # Remover texto em negrito mas manter conteúdo
            (r'\*\*([^*]+)\*\*', r'\1'),

            # Remover "Ele é responsável" e variações
            (r'^[Éé] responsável por ', ''),
            (r'^responsável por ', ''),
            (r'^Ele é responsável por ', ''),
            (r'^Ele é responsável pelo ', ''),
            (r'^que é responsável por ', ''),
            (r'Ele é responsável por ', ''),
            (r'^Ele processa ', 'Processa '),
            (r'^Ele lê ', 'Lê '),
            (r'^Ele realiza ', 'Realiza '),
            (r'^Em Java que ', ''),
            (r'^que realiza ', 'Realiza '),
            (r'^que processa ', 'Processa '),
            (r'^que executa ', 'Executa '),
            (r'^Que automatiza ', 'Automatiza '),
            (r'^Que realiza ', 'Realiza '),
            (r'^Que executa ', 'Executa '),
            (r'^Um componente que ', ''),
            (r'^Um projeto ', ''),
            (r'^Um aplicativo que ', ''),
            (r'Processador de desenvolvido', 'Processador desenvolvido'),
            (r'utilizando um para ', 'para '),
            (r'\. e integra-se', ', integra-se'),
            (r'\. e RabbitMQ', ' com RabbitMQ'),
            (r'Ele processa ', 'Processa '),

            # Limpar espaços e pontuação extras
            (r'\s+', ' '),
            (r'^\s*[,\.]\s*', ''),
            (r'\s*[,\.]\s*$', ''),
            (r'^\s+', ''),
            (r'\s+$', ''),
        ]

        function_text = raw_text
        for pattern, replacement in cleanups:
            function_text = re.sub(pattern, replacement, function_text, flags=re.IGNORECASE)

        # Normalizar espaços
        function_text = re.sub(r'\s+', ' ', function_text).strip()

        # Capitalizar primeira letra
        if function_text and len(function_text) > 1:
            function_text = function_text[0].upper() + function_text[1:]

        # Se ficou muito curto ou sem conteúdo útil, usar inferência
        if len(function_text) < 25 or function_text.lower().startswith('de '):
            return infer_function_from_name(component_name)

        # Limitar tamanho
        if len(function_text) > 150:
            function_text = function_text[:147]
            last_space = function_text.rfind(' ')
            if last_space > 100:
                function_text = function_text[:last_space] + '...'
            else:
                function_text = function_text + '...'

        return function_text.strip()

    except Exception as e:
        return infer_function_from_name(component_name)


def infer_object_from_name(component_name):
    """Infere o objeto/entidade principal do nome do componente."""
    name = component_name.lower()

    # Mapeamento de palavras-chave para objetos
    mappings = {
        'pagamento': 'pagamentos',
        'pagmt': 'pagamentos',
        'transf': 'transferências',
        'ted': 'transferências TED',
        'tef': 'transferências TEF',
        'pix': 'transações PIX',
        'boleto': 'boletos',
        'bol': 'boletos',
        'tributo': 'tributos',
        'tribut': 'tributos',
        'tarifa': 'tarifas',
        'tarif': 'tarifas',
        'extrato': 'extratos',
        'saldo': 'saldos',
        'limite': 'limites',
        'agendamento': 'agendamentos',
        'agendmt': 'agendamentos',
        'notifica': 'notificações',
        'dda': 'boletos DDA',
        'conta': 'contas',
        'cliente': 'clientes',
        'favorecido': 'favorecidos',
        'contato': 'contatos',
        'debito': 'débitos',
        'credito': 'créditos',
        'estorno': 'estornos',
        'devolucao': 'devoluções',
        'comprovante': 'comprovantes',
        'relatorio': 'relatórios',
        'qrcode': 'QR Codes',
        'chave': 'chaves',
        'dict': 'chaves DICT',
    }

    for key, value in mappings.items():
        if key in name:
            return value

    return 'transações'


def infer_function_from_name(component_name):
    """Infere a função do componente baseado no nome."""
    name = component_name.lower()

    # Identificar tipo de componente pelo prefixo
    tipo = ""
    if '-atom-' in name:
        tipo = "Serviço atômico para"
    elif '-orch-' in name:
        tipo = "Orquestrador de"
    elif 'batch' in name:
        tipo = "Processamento batch de"
    elif '-acl-' in name:
        tipo = "Camada de integração para"
    elif '-bff-' in name:
        tipo = "Backend for Frontend de"
    elif name.startswith('ang-'):
        tipo = "Interface web para"
    else:
        tipo = "Gerenciamento de"

    obj = infer_object_from_name(component_name)
    return f"{tipo} {obj}"


def classify_domain(description, component_name):
    """Classifica o componente em um domínio baseado na descrição e nome."""
    text = (description + " " + component_name).lower()
    name_lower = component_name.lower()

    # REGRAS PRIORITÁRIAS (baseadas no nome do componente - mais confiáveis)
    # Ordem importa! Mais específico primeiro

    # Agendamento e Recorrência (02.01) - alta prioridade
    if any(x in name_lower for x in ['agendamento', 'agendado', 'schedule', 'agendmt', 'recorr']):
        return "02.01 - Agendamento e Recorrência"
    if 'débito automático' in text or 'debito automatico' in text or 'deb-aut' in name_lower:
        return "02.01 - Agendamento e Recorrência"

    # Open Finance / Iniciação de Pagamentos (06.01)
    if any(x in name_lower for x in ['open-banking', 'openbanking', 'open-finance']):
        return "06.01 - Iniciação de Pagamentos"

    # DDA (04.06)
    if any(x in name_lower for x in ['dda', 'boletodda']):
        return "04.06 - DDA (Débito Direto Autorizado)"

    # Tributos (04.09)
    if any(x in name_lower for x in ['tribut', '-iss', 'iss-', 'iof', 'fiscal', 'darf', 'gps']):
        return "04.09 - Tributos"

    # Tarifas (04.08)
    if any(x in name_lower for x in ['tarif', 'tarifador']):
        return "04.08 - Tarifas"

    # Limites (04.02)
    if any(x in name_lower for x in ['limite', 'limites']):
        return "04.02 - Limites"

    # Notificações e Relatórios (04.05)
    if any(x in name_lower for x in ['notifica', 'email', 'sms', 'relatorio']):
        return "04.05 - Notificações e Relatórios"

    # Comprovantes (04.04)
    if any(x in name_lower for x in ['comprovante', 'recibo', 'autenticacao']):
        return "04.04 - Comprovantes"

    # Favorecidos (04.01)
    if any(x in name_lower for x in ['favorecido', 'contato', 'beneficiario']):
        return "04.01 - Favorecidos"

    # Autorizações (04.07)
    if any(x in name_lower for x in ['autorizador', 'autoriza']):
        return "04.07 - Autorizações"

    # Dados e Monitoramento (05.01)
    if any(x in name_lower for x in ['cockpit', 'dash', 'monitor', 'health']):
        return "05.01 - Dados e Monitoramento"

    # Logs e Auditoria (05.02)
    if any(x in name_lower for x in ['-log', 'log-', 'audit', 'historico']):
        return "05.02 - Logs e Auditoria"

    # Instrumentos de Pagamento (02.04) - emissão de boletos/QR
    if any(x in name_lower for x in ['gera-boleto', 'emite-boleto', 'qrcode', 'qr-code', 'cobranca']):
        return "02.04 - Instrumentos de Pagamento"

    # Processamento de Recebimento (02.05)
    if any(x in name_lower for x in ['cash-in', 'cashin', 'recebimento', 'baixa-efetiva']):
        return "02.05 - Processamento de Recebimento"

    # Validações (02.02)
    if any(x in name_lower for x in ['validar', 'valida', 'validacao', '-val-']):
        return "02.02 - Validações de Pagamento"

    # Informações Corporativas (03.01)
    if any(x in name_lower for x in ['tabela', 'parametr', 'config', 'cadastro']):
        return "03.01 - Informações Corporativas"

    # ANÁLISE BASEADA NA DESCRIÇÃO (segunda prioridade)
    scores = {}
    for codigo, info in DOMINIOS.items():
        score = 0
        for keyword in info["keywords"]:
            kw = keyword.lower()
            if kw in text:
                # Peso maior para palavras mais específicas e longas
                weight = len(keyword.split()) * 2
                # Bonus se aparecer no nome do componente
                if kw in name_lower:
                    weight += 3
                score += weight
        scores[codigo] = score

    # Encontrar o domínio com maior score (se > threshold)
    if scores:
        best = max(scores, key=scores.get)
        if scores[best] >= 4:  # Threshold mínimo
            return f"{best} - {DOMINIOS[best]['nome']}"

    # DEFAULT: Transação e Processamento (02.03) - o mais comum
    return "02.03 - Transação e Processamento"


def main():
    fichas_dir = Path("FICHAS")
    output_file = "resumo_engenharia_reversa.csv"

    rows = []

    # Iterar por cada sigla (pasta)
    for sigla_dir in sorted(fichas_dir.iterdir()):
        if not sigla_dir.is_dir():
            continue

        sigla = sigla_dir.name
        sigla_desc = SIGLAS_DESC.get(sigla, sigla)

        # Iterar por cada ficha na pasta
        for ficha_file in sorted(sigla_dir.glob("*.md")):
            component_name = ficha_file.stem.replace("_ficha", "")
            description = extract_description(ficha_file)
            function = extract_function(ficha_file, component_name)
            technology = extract_technology(ficha_file, component_name)
            domain = classify_domain(description, component_name)

            rows.append({
                "Sigla": sigla,
                "Descrição da Sigla": sigla_desc,
                "Componente": component_name,
                "Função": function,
                "Descrição do Componente": description,
                "Tecnologia": technology,
                "Domínio Funcional": domain
            })

    # Escrever CSV com BOM para Excel reconhecer UTF-8 corretamente
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Sigla", "Descrição da Sigla", "Componente", "Função",
            "Descrição do Componente", "Tecnologia", "Domínio Funcional"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Total de componentes processados: {len(rows)}")
    print(f"Arquivo gerado: {output_file}")

    # Estatísticas por tecnologia
    tech_counts = {}
    for row in rows:
        t = row["Tecnologia"]
        tech_counts[t] = tech_counts.get(t, 0) + 1

    print("\nDistribuição por Tecnologia:")
    for tech, count in sorted(tech_counts.items(), key=lambda x: -x[1]):
        print(f"  {tech}: {count}")

    # Estatísticas por domínio
    domain_counts = {}
    for row in rows:
        d = row["Domínio Funcional"]
        domain_counts[d] = domain_counts.get(d, 0) + 1

    print("\nDistribuição por Domínio:")
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count}")


if __name__ == "__main__":
    main()
