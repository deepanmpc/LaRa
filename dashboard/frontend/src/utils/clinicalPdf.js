function escapePdfText(text) {
    return String(text)
        .replace(/\\/g, '\\\\')
        .replace(/\(/g, '\\(')
        .replace(/\)/g, '\\)')
        .replace(/\r/g, '')
        .replace(/\n/g, ' ');
}

function buildTextStream(title, lines) {
    const commands = [
        // Institution Header
        'BT',
        '/F1 16 Tf',
        '48 760 Td',
        '(LaRa CLINICAL INTELLIGENCE CENTER) Tj',
        'ET',

        // Subheader
        'BT',
        '/F1 10 Tf',
        '48 744 Td',
        '(OFFICIAL EVALUATION DATA - CLINICIAN USE ONLY) Tj',
        'ET',

        // Status / Date
        'BT',
        '/F1 10 Tf',
        '450 760 Td',
        '(CONFIDENTIAL) Tj',
        'ET',
        'BT',
        '/F1 9 Tf',
        '450 744 Td',
        `(${new Date().toLocaleDateString()}) Tj`,
        'ET',

        // Divider Line
        '1 w',
        '48 728 m',
        '564 728 l',
        'S',

        // Main Report Title
        'BT',
        '/F1 22 Tf',
        '48 695 Td',
        `(${escapePdfText(title.toUpperCase())}) Tj`,
        'ET'
    ];

    let currentY = 650;
    lines.forEach((line) => {
        const isHeader = line.includes(':') && line.length < 40;
        const fontSize = isHeader ? 11 : 11;
        const font = isHeader ? '/F1' : '/F1'; // Note: F1 is Helvetica, we don't have separate bold in this basic setup
        
        commands.push('BT');
        commands.push(`${font} ${fontSize} Tf`);
        commands.push(`48 ${currentY} Td`);
        commands.push(`(${escapePdfText(line)}) Tj`);
        commands.push('ET');
        currentY -= 20;

        if (line.includes('interpretation')) {
            currentY -= 10; // Extra padding after summary
        }
    });

    // Signature Block Placeholder
    currentY -= 40;
    if (currentY > 80) {
        commands.push('BT');
        commands.push('/F1 9 Tf');
        commands.push(`48 ${currentY} Td`);
        commands.push('(VERIFIED AUTOMATICALLY BY LaRa CLINICAL DASHBOARD) Tj');
        commands.push('ET');
    }

    return commands.join('\n');
}

function buildPdfDocument(title, lines) {
    const stream = buildTextStream(title, lines);
    const objects = [
        '1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
        '2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
        '3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj',
        '4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj',
        `5 0 obj << /Length ${stream.length} >> stream\n${stream}\nendstream\nendobj`
    ];

    let pdf = '%PDF-1.4\n';
    const offsets = [0];

    objects.forEach((object) => {
        offsets.push(pdf.length);
        pdf += `${object}\n`;
    });

    const xrefOffset = pdf.length;
    pdf += `xref\n0 ${objects.length + 1}\n`;
    pdf += '0000000000 65535 f \n';

    offsets.slice(1).forEach((offset) => {
        pdf += `${String(offset).padStart(10, '0')} 00000 n \n`;
    });

    pdf += `trailer << /Size ${objects.length + 1} /Root 1 0 R >>\n`;
    pdf += `startxref\n${xrefOffset}\n%%EOF`;

    return pdf;
}

export function downloadClinicalReportPdf(title, lines) {
    const pdfDocument = buildPdfDocument(title, lines);
    const blob = new Blob([pdfDocument], { type: 'application/pdf' });
    const downloadUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');

    anchor.href = downloadUrl;
    anchor.download = `${title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.pdf`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(downloadUrl);
}
