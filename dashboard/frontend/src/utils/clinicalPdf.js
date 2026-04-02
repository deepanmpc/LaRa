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
        'BT',
        '/F1 20 Tf',
        '48 760 Td',
        `(${escapePdfText(title)}) Tj`,
        'ET'
    ];

    let currentY = 730;
    lines.forEach((line) => {
        commands.push('BT');
        commands.push('/F1 11 Tf');
        commands.push(`48 ${currentY} Td`);
        commands.push(`(${escapePdfText(line)}) Tj`);
        commands.push('ET');
        currentY -= 22;
    });

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
