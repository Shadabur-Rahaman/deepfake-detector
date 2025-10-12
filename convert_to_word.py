#!/usr/bin/env python3
"""
Convert Markdown file to Word document
"""

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

def convert_markdown_to_word(md_file, output_file):
    """Convert markdown file to Word document"""
    
    # Read the markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a new Word document
    doc = Document()
    
    # Set up styles
    title_style = doc.styles['Title']
    title_style.font.size = Inches(0.3)
    title_style.font.bold = True
    
    heading1_style = doc.styles['Heading 1']
    heading1_style.font.size = Inches(0.25)
    heading1_style.font.bold = True
    
    heading2_style = doc.styles['Heading 2']
    heading2_style.font.size = Inches(0.22)
    heading2_style.font.bold = True
    
    heading3_style = doc.styles['Heading 3']
    heading3_style.font.size = Inches(0.2)
    heading3_style.font.bold = True
    
    # Split content into lines
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('# '):
            # Main title
            title = line[2:].strip()
            doc.add_heading(title, level=0)
            
        elif line.startswith('## '):
            # Section heading
            heading = line[3:].strip()
            doc.add_heading(heading, level=1)
            
        elif line.startswith('### '):
            # Subsection heading
            heading = line[4:].strip()
            doc.add_heading(heading, level=2)
            
        elif line.startswith('#### '):
            # Sub-subsection heading
            heading = line[5:].strip()
            doc.add_heading(heading, level=3)
            
        elif line.startswith('- '):
            # Bullet point
            bullet_text = line[2:].strip()
            # Remove markdown formatting
            bullet_text = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
            bullet_text = re.sub(r'\*(.*?)\*', r'\1', bullet_text)
            bullet_text = re.sub(r'`(.*?)`', r'\1', bullet_text)
            p = doc.add_paragraph(bullet_text, style='List Bullet')
            
        elif line.startswith('```'):
            # Code block - skip for now
            i += 1
            continue
            
        elif line.startswith('|'):
            # Table - create a simple table
            table_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('|'):
                table_lines.append(lines[j].strip())
                j += 1
            
            if len(table_lines) > 2:  # Has header and data
                # Parse table
                rows = []
                for table_line in table_lines:
                    if '|' in table_line:
                        cells = [cell.strip() for cell in table_line.split('|')[1:-1]]
                        rows.append(cells)
                
                if len(rows) > 1:
                    # Create table
                    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                    table.style = 'Table Grid'
                    
                    for row_idx, row_data in enumerate(rows):
                        for col_idx, cell_data in enumerate(row_data):
                            if col_idx < len(table.rows[row_idx].cells):
                                table.rows[row_idx].cells[col_idx].text = cell_data
                    
                    i = j - 1
            
        elif line and not line.startswith('---'):
            # Regular paragraph
            # Clean up markdown formatting
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)
            clean_text = re.sub(r'`(.*?)`', r'\1', clean_text)
            clean_text = re.sub(r'✅', '✓', clean_text)
            clean_text = re.sub(r'❌', '✗', clean_text)
            clean_text = re.sub(r'⚠️', '⚠', clean_text)
            clean_text = re.sub(r'🚀', '🚀', clean_text)
            clean_text = re.sub(r'🔧', '🔧', clean_text)
            clean_text = re.sub(r'📊', '📊', clean_text)
            clean_text = re.sub(r'🎯', '🎯', clean_text)
            clean_text = re.sub(r'💡', '💡', clean_text)
            clean_text = re.sub(r'🛠️', '🛠️', clean_text)
            clean_text = re.sub(r'📦', '📦', clean_text)
            clean_text = re.sub(r'🔍', '🔍', clean_text)
            clean_text = re.sub(r'🌐', '🌐', clean_text)
            clean_text = re.sub(r'📞', '📞', clean_text)
            clean_text = re.sub(r'📁', '📁', clean_text)
            clean_text = re.sub(r'🧪', '🧪', clean_text)
            clean_text = re.sub(r'🐛', '🐛', clean_text)
            clean_text = re.sub(r'🆘', '🆘', clean_text)
            clean_text = re.sub(r'🎉', '🎉', clean_text)
            
            if clean_text.strip():
                doc.add_paragraph(clean_text)
        
        i += 1
    
    # Save the document
    doc.save(output_file)
    print(f'Word document created successfully: {output_file}')

if __name__ == "__main__":
    convert_markdown_to_word('A_FINAL_PROJECT_REPORT.md', 'A_FINAL_PROJECT_REPORT.docx')
