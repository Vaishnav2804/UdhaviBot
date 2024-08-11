# UdhaviBot (உதவிBot - உதவி பொறி - HelpBot) 

UdhaviBot is a chatbot designed to assist and empower underserved individuals by providing information on government policies related to education, healthcare (with a focus on maternal and children), agriculture, insurance and many government schemes. The chatbot aims to bridge the information gap and help users access the support and resources they need.

## Technologies Used
- Backend: Python
- Frontend: React, HTML, CSS, JavaScript
- Natural Language Processing: Gemini, spaCy
- Retrieval-Augmented Generation (RAG): Combining LLM and RAG for enhanced information retrieval and response generation
- Vector Database: Chroma DB
- LLM: Gemini 1.5 Pro API Key
- Embedding: GoogleGenerativeAIEmbeddings

## How to Run Python Code:
1. Install Python [Python Installation](https://www.python.org/downloads/)
2. Git clone this repository
3. Create a new virtualenv:
    ```bash
    python3 -m venv venv
    source ./venv/bin/activate
    ```
4. Install all required libraries from `requirements.txt`
    ```bash
    pip install -r requirements.txt
    ```
5. Run python app
    ```bash
    python3 app.py
    ```

## Introduction to the Problem
Imagine millions of people across India—rural villagers, senior citizens, and the underserved—struggling to access vital government schemes simply because the information is buried in complex documents or not available in their language. This is a massive barrier to the benefits they are entitled to.

## Solution Overview
But what if there was a solution that could break down these barriers? We’ve built Udhavi Bot, a revolutionary voice-based conversational system powered by Gemini LLM, designed to make 2,980 government schemes easily accessible to everyone, in any of India’s vernacular languages.

## How It Works

We meticulously scraped the web for every detail on these government schemes—their benefits, eligibility criteria, age and gender requirements, application processes, and documentation needed.
We then vectorized this information, allowing our system to retrieve and communicate relevant data instantly.
Technology Behind the Scenes
The magic happens with our integration of Google APIs. We use Google’s speech-to-text and translate technologies to ensure that anyone, regardless of language or literacy level, can interact with our system seamlessly. Whether someone speaks Hindi, Tamil, Bengali, or any other regional language, Udhavi Bot understands and responds in real-time.

## Real-World Impact
Picture a farmer in a remote village who needs financial aid for his crops. He can simply speak into Udhavi Bot in his native language, and within seconds, he’ll receive detailed instructions on how to apply for the relevant scheme—no bureaucratic maze, no language barrier. This is not just a tool; it’s a lifeline, making government benefits truly accessible to the masses.

## Global Scalability
While Udhavi Bot is currently tailored for India, the underlying technology is universally applicable. Imagine this system scaled across the world, where citizens in any country could access their government’s services in their own language. With slight customization, this solution can empower people everywhere to access vital information, breaking down linguistic and bureaucratic barriers globally.

## Showcasing the Power of Google APIs
Our use of Google’s powerful APIs doesn’t just end at accessibility. The seamless integration allows for a smooth, intuitive experience, demonstrating how cutting-edge technology can solve real-world problems. This project is a testament to how Google’s tools can be leveraged to create meaningful change at scale.

## Call to Action
In a country as diverse as India, where over a billion people speak hundreds of languages, Udhavi Bot represents a giant leap forward in bridging the gap between government services and the people who need them most. It’s not just about technology; it’s about empowerment. We’re enabling citizens to claim their rights and benefits, with dignity and ease.

## Conclusion
This is more than a project. It’s a mission to transform how government schemes reach the people of India—and potentially the entire world. With your support, we can make sure that no one is left behind, no matter where they live or what language they speak.





## Contributing
We welcome contributions from the community. To contribute to UdhaviBot, follow these steps:
1. Fork the repository.
2. Create a new branch: 
```bash
git checkout -b feature/your-feature-name
```
3. Make your changes.
4. Commit your changes:
```bash
git commit -m 'Add some feature'
```
5. Push to the branch:
```bash
git push origin feature/your-feature-name
```
6. Open a pull request.

## Contact
For any questions or feedback, please contact us at vaishnavvaidheeswaran@gmail.com

