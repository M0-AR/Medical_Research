from report_generator import generate_report

# Sample data
test_papers = [
    {
        'title': 'Novel Treatment for Chronic Pain Using AI-guided Drug Delivery',
        'abstract': 'This study presents a breakthrough in chronic pain management using AI-controlled drug delivery systems. The system adapts medication dosage based on real-time patient data, resulting in better pain control and fewer side effects.',
        'authors': 'John Smith, Maria Garcia, Robert Johnson',
        'year': '2024',
        'source': 'PubMed',
        'summary_gpt4': 'The research introduces an innovative AI-powered drug delivery system for chronic pain management. The system uses machine learning to optimize medication dosage based on patient vital signs and reported pain levels. Clinical trials showed a 45% improvement in pain control compared to traditional methods.',
        'summary_claude': 'A novel approach to pain management utilizing artificial intelligence to control drug delivery. The system continuously monitors patient data and adjusts medication levels accordingly. Results demonstrate significant improvements in pain control while reducing adverse effects.'
    },
    {
        'title': 'Early Detection of Alzheimer\'s Disease Using Advanced Brain Imaging',
        'abstract': 'We developed a new imaging technique combining MRI and PET scans with machine learning analysis to detect early signs of Alzheimer\'s disease. The method shows 92% accuracy in identifying pre-symptomatic cases.',
        'authors': 'Sarah Williams, James Chen',
        'year': '2024',
        'source': 'ClinicalTrials.gov',
        'summary_gpt4': 'This groundbreaking study combines advanced imaging techniques with AI analysis to enable early Alzheimer\'s detection. The method can identify disease markers years before symptoms appear, potentially allowing for earlier intervention.',
        'summary_claude': 'Research presents a novel diagnostic approach combining multiple brain imaging modalities with machine learning. The technique achieves high accuracy in detecting Alzheimer\'s disease before clinical symptoms manifest.'
    },
    {
        'title': 'Breakthrough in CRISPR Gene Therapy for Rare Genetic Disorders',
        'abstract': 'Our team successfully developed a modified CRISPR-Cas9 system that can correct multiple genetic mutations simultaneously. The technique shows promising results in treating several rare genetic disorders with minimal off-target effects.',
        'authors': 'David Kim, Lisa Patel, Michael Brown',
        'year': '2024',
        'source': 'medRxiv',
        'summary_gpt4': 'A significant advancement in gene therapy using an enhanced CRISPR system. The modified technique can address multiple genetic mutations in a single treatment while maintaining high precision and safety.',
        'summary_claude': 'The study presents an improved CRISPR-based gene editing approach capable of correcting multiple genetic defects simultaneously. Initial trials show promising results with high efficiency and safety profiles.'
    }
]

if __name__ == "__main__":
    print("Generating test report...")
    report_file = generate_report(test_papers, 'test_medical_report.pdf')
    if report_file:
        print(f"Test report generated successfully: {report_file}")
    else:
        print("Failed to generate test report")
