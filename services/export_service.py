"""
Export Service for PersonalizedReddit
Handles data export in multiple formats with professional templates
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import tempfile

try:
    import pandas as pd
    pandas_available = True
except ImportError:
    pandas_available = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    reportlab_available = True
except ImportError:
    reportlab_available = False

from utils.logging_config import get_logger, log_performance

class ExportService:
    """
    Professional data export service supporting multiple formats
    """
    
    def __init__(self, database=None):
        self.database = database
        self.logger = get_logger(__name__)
        
        # Export configuration
        self.export_dir = Path("Exports")
        self.export_dir.mkdir(exist_ok=True)
        
        # Templates and formatting
        self.templates = {
            'business_leads': {
                'columns': [
                    'title', 'author', 'subreddit', 'business_score', 'urgency_level',
                    'problem_indicators', 'created_date', 'permalink'
                ],
                'headers': [
                    'Title', 'Author', 'Subreddit', 'Business Score', 'Urgency',
                    'Problem Keywords', 'Date', 'Reddit Link'
                ]
            },
            'newsletter_digest': {
                'columns': [
                    'title', 'summary', 'subreddit', 'priority', 'business_score',
                    'engagement_score', 'created_date'
                ],
                'headers': [
                    'Opportunity Title', 'Summary', 'Source', 'Priority', 
                    'Business Score', 'Engagement', 'Date'
                ]
            },
            'subreddit_recommendations': {
                'columns': [
                    'subreddit', 'category', 'match_percentage', 'members',
                    'activity_level', 'explanation'
                ],
                'headers': [
                    'Subreddit', 'Category', 'Match %', 'Members',
                    'Activity', 'Why Recommended'
                ]
            }
        }
    
    @log_performance
    def export_data(self, data: Union[List[Dict], Dict], filename: str, 
                   format: str = "csv", template: str = None) -> Path:
        """
        Export data to specified format
        
        Args:
            data: Data to export (list of dicts or single dict)
            filename: Base filename (without extension)
            format: Export format (csv, json, excel, markdown, pdf)
            template: Template to use for formatting
            
        Returns:
            Path to exported file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == "csv":
                return self._export_csv(data, f"{filename}_{timestamp}.csv", template)
            elif format.lower() == "json":
                return self._export_json(data, f"{filename}_{timestamp}.json")
            elif format.lower() == "excel":
                return self._export_excel(data, f"{filename}_{timestamp}.xlsx", template)
            elif format.lower() == "markdown":
                return self._export_markdown(data, f"{filename}_{timestamp}.md", template)
            elif format.lower() == "pdf":
                return self._export_pdf(data, f"{filename}_{timestamp}.pdf", template)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Export failed: {e}", exc_info=True)
            raise
    
    def _export_csv(self, data: Union[List[Dict], Dict], filename: str, template: str = None) -> Path:
        """Export data to CSV format"""
        filepath = self.export_dir / filename
        
        # Convert single dict to list
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            raise ValueError("No data to export")
        
        # Get template configuration
        template_config = self.templates.get(template, {})
        columns = template_config.get('columns', list(data[0].keys()))
        headers = template_config.get('headers', columns)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers
            writer.writerow(headers)
            
            # Write data rows
            for row in data:
                csv_row = []
                for col in columns:
                    value = row.get(col, '')
                    
                    # Handle list/dict values
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value) if isinstance(value, dict) else '; '.join(map(str, value))
                    
                    csv_row.append(str(value))
                
                writer.writerow(csv_row)
        
        self.logger.info(f"Exported {len(data)} records to CSV: {filepath}")
        return filepath
    
    def _export_json(self, data: Union[List[Dict], Dict], filename: str) -> Path:
        """Export data to JSON format"""
        filepath = self.export_dir / filename
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'record_count': len(data) if isinstance(data, list) else 1,
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Exported data to JSON: {filepath}")
        return filepath
    
    def _export_excel(self, data: Union[List[Dict], Dict], filename: str, template: str = None) -> Path:
        """Export data to Excel format"""
        if not pandas_available:
            self.logger.warning("Pandas not available, falling back to CSV")
            return self._export_csv(data, filename.replace('.xlsx', '.csv'), template)
        
        filepath = self.export_dir / filename
        
        # Convert to DataFrame
        if isinstance(data, dict):
            data = [data]
        
        df = pd.DataFrame(data)
        
        # Apply template if specified
        template_config = self.templates.get(template, {})
        if template_config:
            columns = template_config.get('columns', df.columns)
            headers = template_config.get('headers', columns)
            
            # Reorder columns and rename headers
            df = df[columns] if all(col in df.columns for col in columns) else df
            df.columns = headers[:len(df.columns)]
        
        # Export with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            
            # Add metadata sheet
            metadata = pd.DataFrame({
                'Property': ['Export Date', 'Record Count', 'Template Used'],
                'Value': [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(data), template or 'None']
            })
            metadata.to_excel(writer, index=False, sheet_name='Metadata')
        
        self.logger.info(f"Exported {len(data)} records to Excel: {filepath}")
        return filepath
    
    def _export_markdown(self, data: Union[List[Dict], Dict], filename: str, template: str = None) -> Path:
        """Export data to Markdown format"""
        filepath = self.export_dir / filename
        
        if isinstance(data, dict):
            data = [data]
        
        with open(filepath, 'w', encoding='utf-8') as mdfile:
            # Write header
            mdfile.write(f"# {filename.replace('.md', '').replace('_', ' ').title()}\n\n")
            mdfile.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            mdfile.write(f"**Total Records:** {len(data)}\n\n")
            mdfile.write("---\n\n")
            
            # Write data based on template or generic format
            if template == 'business_leads':
                self._write_business_leads_markdown(mdfile, data)
            elif template == 'newsletter_digest':
                self._write_newsletter_markdown(mdfile, data)
            elif template == 'subreddit_recommendations':
                self._write_recommendations_markdown(mdfile, data)
            else:
                self._write_generic_markdown(mdfile, data)
        
        self.logger.info(f"Exported {len(data)} records to Markdown: {filepath}")
        return filepath
    
    def _write_business_leads_markdown(self, file, data: List[Dict]):
        """Write business leads in Markdown format"""
        for i, lead in enumerate(data, 1):
            file.write(f"## {i}. {lead.get('title', 'Untitled')}\n\n")
            file.write(f"**Subreddit:** r/{lead.get('subreddit', 'unknown')}  \n")
            file.write(f"**Author:** u/{lead.get('author', 'unknown')}  \n")
            file.write(f"**Business Score:** {lead.get('business_score', 0)}/10  \n")
            file.write(f"**Urgency:** {lead.get('urgency_level', 'low').title()}  \n")
            
            if lead.get('problem_indicators'):
                indicators = lead['problem_indicators']
                if isinstance(indicators, list):
                    file.write(f"**Keywords:** {', '.join(indicators)}  \n")
                else:
                    file.write(f"**Keywords:** {indicators}  \n")
            
            file.write(f"**Date:** {lead.get('created_date', 'Unknown')}  \n")
            
            if lead.get('permalink'):
                file.write(f"**Link:** {lead['permalink']}\n\n")
            
            if lead.get('summary'):
                file.write(f"**Summary:**\n{lead['summary']}\n\n")
            
            file.write("---\n\n")
    
    def _write_newsletter_markdown(self, file, data: List[Dict]):
        """Write newsletter digest in Markdown format"""
        # Group by priority
        high_priority = [d for d in data if d.get('priority') == 'high']
        medium_priority = [d for d in data if d.get('priority') == 'medium']
        low_priority = [d for d in data if d.get('priority') == 'low']
        
        for priority_name, items in [('High Priority', high_priority), 
                                   ('Medium Priority', medium_priority), 
                                   ('Low Priority', low_priority)]:
            if items:
                file.write(f"## {priority_name} Opportunities\n\n")
                for item in items:
                    file.write(f"### {item.get('title', 'Untitled')}\n")
                    file.write(f"**Source:** r/{item.get('subreddit')} | ")
                    file.write(f"**Score:** {item.get('business_score', 0)} | ")
                    file.write(f"**Engagement:** {item.get('engagement_score', 0)}\n\n")
                    
                    if item.get('summary'):
                        file.write(f"{item['summary']}\n\n")
                    
                    file.write("---\n\n")
    
    def _write_recommendations_markdown(self, file, data: List[Dict]):
        """Write subreddit recommendations in Markdown format"""
        for rec in data:
            file.write(f"## r/{rec.get('subreddit', 'unknown')}\n\n")
            file.write(f"**Category:** {rec.get('category', 'Unknown')}  \n")
            file.write(f"**Match Score:** {rec.get('match_percentage', 0)}%  \n")
            file.write(f"**Members:** {rec.get('members', 'Unknown')}  \n")
            file.write(f"**Activity Level:** {rec.get('activity_level', 'Unknown')}  \n")
            
            if rec.get('explanation'):
                file.write(f"**Why Recommended:** {rec['explanation']}  \n")
            
            file.write("\n---\n\n")
    
    def _write_generic_markdown(self, file, data: List[Dict]):
        """Write generic data in Markdown table format"""
        if not data:
            return
        
        # Get all unique keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        keys = sorted(list(all_keys))
        
        # Write table header
        file.write("| " + " | ".join(keys) + " |\n")
        file.write("| " + " | ".join(["---"] * len(keys)) + " |\n")
        
        # Write data rows
        for item in data:
            row = []
            for key in keys:
                value = item.get(key, '')
                if isinstance(value, (list, dict)):
                    value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                row.append(str(value))
            file.write("| " + " | ".join(row) + " |\n")
    
    def _export_pdf(self, data: Union[List[Dict], Dict], filename: str, template: str = None) -> Path:
        """Export data to PDF format"""
        if not reportlab_available:
            self.logger.warning("ReportLab not available, falling back to Markdown")
            return self._export_markdown(data, filename.replace('.pdf', '.md'), template)
        
        filepath = self.export_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2E4057')
        )
        
        title = filename.replace('.pdf', '').replace('_', ' ').title()
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata_text = f"""
        <b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Record Count:</b> {len(data) if isinstance(data, list) else 1}<br/>
        <b>Template:</b> {template or 'Generic'}
        """
        story.append(Paragraph(metadata_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        if isinstance(data, dict):
            data = [data]
        
        # Create table data
        if template and template in self.templates:
            template_config = self.templates[template]
            columns = template_config['columns']
            headers = template_config['headers']
        else:
            columns = list(data[0].keys()) if data else []
            headers = columns
        
        table_data = [headers]
        
        for row in data:
            table_row = []
            for col in columns:
                value = row.get(col, '')
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)[:50] + "..." if len(json.dumps(value)) > 50 else json.dumps(value)
                
                # Truncate long text
                value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                table_row.append(value)
            
            table_data.append(table_row)
        
        # Create and style table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD'))
        ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        
        self.logger.info(f"Exported {len(data)} records to PDF: {filepath}")
        return filepath
    
    def export_business_leads(self, leads: List[Dict], format: str = "csv") -> Path:
        """Export business leads with specialized formatting"""
        return self.export_data(leads, "business_leads", format, "business_leads")
    
    def export_newsletter_digest(self, digest: Dict, format: str = "markdown") -> Path:
        """Export newsletter digest"""
        # Extract opportunities from digest
        opportunities = digest.get('top_opportunities', [])
        return self.export_data(opportunities, "newsletter_digest", format, "newsletter_digest")
    
    def export_subreddit_recommendations(self, recommendations: List[Dict], format: str = "csv") -> Path:
        """Export subreddit recommendations"""
        return self.export_data(recommendations, "subreddit_recommendations", format, "subreddit_recommendations")
    
    def get_export_history(self, days: int = 30) -> List[Dict]:
        """Get export history from database"""
        if self.database:
            try:
                # This would query the export_history table
                # For now, return simulated data
                pass
            except Exception as e:
                self.logger.error(f"Failed to get export history: {e}")
        
        # Return list of recent exports in the directory
        exports = []
        for file_path in self.export_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                stat = file_path.stat()
                exports.append({
                    'filename': file_path.name,
                    'format': file_path.suffix[1:],
                    'size_bytes': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'file_path': str(file_path)
                })
        
        # Sort by creation time, most recent first
        exports.sort(key=lambda x: x['created_at'], reverse=True)
        return exports[:50]  # Limit to 50 recent exports
    
    def cleanup_old_exports(self, days: int = 30) -> int:
        """Clean up old export files"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in self.export_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_ctime < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to delete {file_path}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} old export files")
        return deleted_count
    
    def close(self):
        """Close the export service"""
        self.logger.info("Export service closed")