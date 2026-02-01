#!/usr/bin/env python3
"""
Script para extrair dados das fichas de componentes e gerar CSV consolidado.
"""

import os
import re
import json
import csv
from pathlib import Path

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
    "SPBB-ISPB": "SPB Bradesco - ISPB"
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
            domain = classify_domain(description, component_name)

            rows.append({
                "Sigla": sigla,
                "Descrição da Sigla": sigla_desc,
                "Componente": component_name,
                "Descrição do Componente": description,
                "Domínio Funcional": domain
            })

    # Escrever CSV com BOM para Excel reconhecer UTF-8 corretamente
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Sigla", "Descrição da Sigla", "Componente",
            "Descrição do Componente", "Domínio Funcional"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Total de componentes processados: {len(rows)}")
    print(f"Arquivo gerado: {output_file}")

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
