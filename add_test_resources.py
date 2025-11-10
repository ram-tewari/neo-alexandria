#!/usr/bin/env python3
"""
Script to add 20+ diverse resources for testing the knowledge graph functionality.
This creates a rich dataset with various topics, subjects, and classifications.
"""

import sqlite3
import uuid
from datetime import datetime, timezone

def add_test_resources():
    """Add diverse test resources to the database."""
    
    # Connect to database
    conn = sqlite3.connect('backend/neo_alexandria.db')
    cursor = conn.cursor()
    
    # Sample resources with diverse topics for rich knowledge graph connections
    resources = [
        # Technology & AI
        {
            'id': str(uuid.uuid4()),
            'title': 'Introduction to Machine Learning',
            'url': 'https://example.com/ml-intro',
            'description': 'A comprehensive guide to machine learning fundamentals, covering supervised and unsupervised learning algorithms.',
            'subjects': ['machine-learning', 'artificial-intelligence', 'data-science'],
            'classification_code': 'TECH.ML.001',
            'content_type': 'tutorial'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Deep Learning with Neural Networks',
            'url': 'https://example.com/deep-learning',
            'description': 'Advanced concepts in deep learning, including convolutional neural networks and recurrent neural networks.',
            'subjects': ['deep-learning', 'neural-networks', 'artificial-intelligence'],
            'classification_code': 'TECH.DL.001',
            'content_type': 'research-paper'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Python for Data Science',
            'url': 'https://example.com/python-ds',
            'description': 'Learn Python programming specifically for data analysis, visualization, and machine learning applications.',
            'subjects': ['python', 'data-science', 'programming'],
            'classification_code': 'TECH.PY.001',
            'content_type': 'tutorial'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Natural Language Processing Fundamentals',
            'url': 'https://example.com/nlp-basics',
            'description': 'Understanding how computers process and understand human language using various NLP techniques.',
            'subjects': ['nlp', 'artificial-intelligence', 'text-processing'],
            'classification_code': 'TECH.NLP.001',
            'content_type': 'tutorial'
        },
        
        # Web Development
        {
            'id': str(uuid.uuid4()),
            'title': 'Modern JavaScript ES6+ Features',
            'url': 'https://example.com/js-es6',
            'description': 'Explore the latest JavaScript features including arrow functions, destructuring, and async/await.',
            'subjects': ['javascript', 'web-development', 'programming'],
            'classification_code': 'WEB.JS.001',
            'content_type': 'tutorial'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'React.js Best Practices',
            'url': 'https://example.com/react-best-practices',
            'description': 'Learn how to build scalable and maintainable React applications with modern patterns and hooks.',
            'subjects': ['react', 'javascript', 'web-development'],
            'classification_code': 'WEB.REACT.001',
            'content_type': 'guide'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'CSS Grid and Flexbox Layout',
            'url': 'https://example.com/css-layout',
            'description': 'Master modern CSS layout techniques using Grid and Flexbox for responsive web design.',
            'subjects': ['css', 'web-design', 'layout'],
            'classification_code': 'WEB.CSS.001',
            'content_type': 'tutorial'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Node.js Backend Development',
            'url': 'https://example.com/nodejs-backend',
            'description': 'Build robust server-side applications using Node.js, Express, and modern backend patterns.',
            'subjects': ['nodejs', 'backend', 'javascript'],
            'classification_code': 'WEB.NODE.001',
            'content_type': 'tutorial'
        },
        
        # Science & Research
        {
            'id': str(uuid.uuid4()),
            'title': 'Quantum Computing Principles',
            'url': 'https://example.com/quantum-computing',
            'description': 'Introduction to quantum mechanics applied to computing, including qubits and quantum algorithms.',
            'subjects': ['quantum-computing', 'physics', 'computer-science'],
            'classification_code': 'SCI.QC.001',
            'content_type': 'research-paper'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Climate Change and Renewable Energy',
            'url': 'https://example.com/climate-energy',
            'description': 'Analysis of climate change impacts and the role of renewable energy technologies in mitigation.',
            'subjects': ['climate-change', 'renewable-energy', 'environment'],
            'classification_code': 'SCI.ENV.001',
            'content_type': 'research-paper'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Biotechnology and Genetic Engineering',
            'url': 'https://example.com/biotech-genetics',
            'description': 'Exploring the latest advances in biotechnology, CRISPR gene editing, and genetic engineering applications.',
            'subjects': ['biotechnology', 'genetics', 'medicine'],
            'classification_code': 'SCI.BIO.001',
            'content_type': 'research-paper'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Space Exploration and Astronomy',
            'url': 'https://example.com/space-astronomy',
            'description': 'Recent discoveries in space exploration, exoplanets, and our understanding of the universe.',
            'subjects': ['space', 'astronomy', 'physics'],
            'classification_code': 'SCI.AST.001',
            'content_type': 'article'
        },
        
        # Business & Economics
        {
            'id': str(uuid.uuid4()),
            'title': 'Digital Transformation in Business',
            'url': 'https://example.com/digital-transformation',
            'description': 'How businesses are adapting to digital technologies and changing market dynamics.',
            'subjects': ['business', 'digital-transformation', 'technology'],
            'classification_code': 'BUS.DT.001',
            'content_type': 'case-study'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Cryptocurrency and Blockchain Technology',
            'url': 'https://example.com/crypto-blockchain',
            'description': 'Understanding cryptocurrencies, blockchain technology, and their impact on finance and business.',
            'subjects': ['cryptocurrency', 'blockchain', 'finance'],
            'classification_code': 'BUS.CRYPTO.001',
            'content_type': 'article'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Startup Funding and Venture Capital',
            'url': 'https://example.com/startup-funding',
            'description': 'Guide to raising capital for startups, understanding venture capital, and funding strategies.',
            'subjects': ['startups', 'venture-capital', 'funding'],
            'classification_code': 'BUS.VC.001',
            'content_type': 'guide'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Remote Work and Digital Nomadism',
            'url': 'https://example.com/remote-work',
            'description': 'The future of work, remote collaboration tools, and the rise of digital nomadism.',
            'subjects': ['remote-work', 'workplace', 'technology'],
            'classification_code': 'BUS.REMOTE.001',
            'content_type': 'article'
        },
        
        # Health & Medicine
        {
            'id': str(uuid.uuid4()),
            'title': 'Precision Medicine and Personalized Healthcare',
            'url': 'https://example.com/precision-medicine',
            'description': 'How genetic testing and AI are revolutionizing personalized treatment approaches.',
            'subjects': ['medicine', 'genetics', 'artificial-intelligence'],
            'classification_code': 'HEALTH.PM.001',
            'content_type': 'research-paper'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Mental Health and Technology',
            'url': 'https://example.com/mental-health-tech',
            'description': 'Exploring digital mental health solutions, therapy apps, and AI-assisted mental health care.',
            'subjects': ['mental-health', 'technology', 'healthcare'],
            'classification_code': 'HEALTH.MH.001',
            'content_type': 'article'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Telemedicine and Remote Healthcare',
            'url': 'https://example.com/telemedicine',
            'description': 'The growth of telemedicine, remote patient monitoring, and virtual healthcare delivery.',
            'subjects': ['telemedicine', 'healthcare', 'technology'],
            'classification_code': 'HEALTH.TELE.001',
            'content_type': 'case-study'
        },
        
        # Education & Learning
        {
            'id': str(uuid.uuid4()),
            'title': 'Online Education and E-Learning Platforms',
            'url': 'https://example.com/online-education',
            'description': 'The evolution of online learning, MOOCs, and digital education platforms.',
            'subjects': ['education', 'e-learning', 'technology'],
            'classification_code': 'EDU.ONLINE.001',
            'content_type': 'article'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Gamification in Learning',
            'url': 'https://example.com/gamification-learning',
            'description': 'How game mechanics and design principles can enhance educational experiences.',
            'subjects': ['education', 'gamification', 'learning'],
            'classification_code': 'EDU.GAME.001',
            'content_type': 'research-paper'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Artificial Intelligence in Education',
            'url': 'https://example.com/ai-education',
            'description': 'Applications of AI in personalized learning, automated grading, and educational analytics.',
            'subjects': ['artificial-intelligence', 'education', 'machine-learning'],
            'classification_code': 'EDU.AI.001',
            'content_type': 'research-paper'
        },
        
        # Additional diverse topics for rich connections
        {
            'id': str(uuid.uuid4()),
            'title': 'Cybersecurity and Threat Intelligence',
            'url': 'https://example.com/cybersecurity',
            'description': 'Modern cybersecurity challenges, threat detection, and protection strategies for digital assets.',
            'subjects': ['cybersecurity', 'information-security', 'technology'],
            'classification_code': 'SEC.CYB.001',
            'content_type': 'guide'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Internet of Things (IoT) Security',
            'url': 'https://example.com/iot-security',
            'description': 'Security challenges and solutions for connected devices in the IoT ecosystem.',
            'subjects': ['iot', 'cybersecurity', 'connected-devices'],
            'classification_code': 'SEC.IOT.001',
            'content_type': 'research-paper'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Augmented Reality and Virtual Reality',
            'url': 'https://example.com/ar-vr',
            'description': 'The future of immersive technologies, AR/VR applications, and mixed reality experiences.',
            'subjects': ['augmented-reality', 'virtual-reality', 'technology'],
            'classification_code': 'TECH.ARVR.001',
            'content_type': 'article'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Edge Computing and Distributed Systems',
            'url': 'https://example.com/edge-computing',
            'description': 'Moving computation closer to data sources, edge computing architectures, and distributed processing.',
            'subjects': ['edge-computing', 'distributed-systems', 'cloud-computing'],
            'classification_code': 'TECH.EDGE.001',
            'content_type': 'tutorial'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Sustainable Technology and Green Computing',
            'url': 'https://example.com/green-computing',
            'description': 'Environmental impact of technology and strategies for sustainable computing practices.',
            'subjects': ['sustainability', 'green-computing', 'environment'],
            'classification_code': 'TECH.GREEN.001',
            'content_type': 'article'
        }
    ]
    
    # Insert resources
    for resource in resources:
        # Convert subjects list to JSON string
        subjects_json = '["' + '","'.join(resource['subjects']) + '"]'
        
        cursor.execute('''
            INSERT INTO resources (
                id, title, description, source, subject, classification_code, 
                type, ingestion_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            resource['id'],
            resource['title'],
            resource['description'],
            resource['url'],  # Using 'source' column for URL
            subjects_json,    # Using 'subject' column for subjects
            resource['classification_code'],
            resource['content_type'],  # Using 'type' column
            'completed',
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"✅ Successfully added {len(resources)} test resources!")
    print("\n📊 Resource breakdown by topic:")
    
    # Count by classification
    topics = {}
    for resource in resources:
        topic = resource['classification_code'].split('.')[0]
        topics[topic] = topics.get(topic, 0) + 1
    
    for topic, count in topics.items():
        print(f"  {topic}: {count} resources")
    
    print(f"\n🎯 Total subjects covered: {len(set(subject for r in resources for subject in r['subjects']))}")
    print("🚀 Your knowledge graph should now have rich connections!")

if __name__ == "__main__":
    add_test_resources()
