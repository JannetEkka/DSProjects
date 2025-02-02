import React from 'react';

const PortfolioApp = () => {
  const projects = [
    {
      title: "Semiconductor Manufacturing Yield Prediction",
      description: "Led the development of a machine learning solution achieving 99.20% accuracy in predicting manufacturing yields using SVC. Engineered feature selection pipeline processing 591 sensor signals.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/Semiconductor_Manufacturing_Prediction_FMT",
      skills: ["Manufacturing Analytics", "Machine Learning", "Python", "Feature Engineering"]
    },
    {
      title: "MultiModel Botanical Classification",
      description: "Developed plant species classification system using computer vision and deep learning, achieving 83.79% accuracy with CNN architecture and transfer learning with EfficientNetB0.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/MultiModel_Botanical_Classification_CV",
      skills: ["Computer Vision", "Deep Learning", "CNN", "TensorFlow"]
    },
    {
      title: "Signal Quality & SVHN Classification",
      description: "Implemented neural networks for signal quality prediction (90% accuracy) and street view house number recognition (85% accuracy) using deep learning.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/Signal_Classification_Digit_Recognition_NNDL",
      skills: ["Deep Learning", "Neural Networks", "Computer Vision", "Signal Processing"]
    },
    {
      title: "Stock Market Sentiment Analysis",
      description: "Built AI-driven financial market intelligence system analyzing news sentiment and automating weekly summaries using ensemble learning and LLMs.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/Stock_Market_Sentiment_Analysis_NLP",
      skills: ["NLP", "Machine Learning", "Sentiment Analysis", "Financial Analysis"]
    },
    {
      title: "New-Wheels Performance Analytics",
      description: "Led end-to-end analytics project analyzing customer behavior and sales patterns across 994 customers and $1.25B revenue, delivering actionable insights.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/New_Wheels_Performance_Analytics_SQL",
      skills: ["Business Intelligence", "SQL", "Data Analysis", "KPI Reporting"]
    },
    {
      title: "YouTube AdView Analytics",
      description: "Developed ML solution to predict advertisement views using engagement metrics, achieving R² of 0.252 with Random Forest Regression.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/YouTube_AdView_Analytics_ML",
      skills: ["Machine Learning", "Python", "Data Analysis", "Regression"]
    },
    {
      title: "Automobile Analysis & Classification",
      description: "Implemented K-means clustering and PCA-enhanced SVM for vehicle segmentation and classification using comprehensive car attributes dataset.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/Automobile_Analysis_Classification_USL",
      skills: ["Machine Learning", "Clustering", "PCA", "Python"]
    },
    {
      title: "Business Analytics Portfolio",
      description: "Built models for used car price prediction (86% accuracy) and employee attrition prediction (84% accuracy) using various ML algorithms.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/Business_Analytics_Portfolio_SL",
      skills: ["Predictive Modeling", "Machine Learning", "Business Analytics"]
    },
    {
      title: "Customer Churn Prediction",
      description: "Developed ensemble learning solution achieving 81.48% accuracy in predicting telecom customer churn using Random Forest optimization.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/Customer_Churn_Prediction_ET",
      skills: ["Machine Learning", "Python", "Ensemble Methods"]
    },
    {
      title: "Applied Statistics Project",
      description: "Implemented statistical analysis covering data manipulation, probability distributions, and hypothesis testing using Python.",
      githubLink: "https://github.com/JannetEkka/DSProjects/tree/main/Applied_Statistics_Project",
      skills: ["Statistics", "Python", "Data Analysis", "Hypothesis Testing"]
    }
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-purple-900 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <img 
            src="./profile pic.png"
            alt="Jannet Akanksha Ekka" 
            className="w-48 h-48 rounded-full mx-auto mb-8 object-cover border-4 border-white"
          />
          <h1 className="text-4xl font-bold mb-4">Jannet Akanksha Ekka</h1>
          <p className="text-xl">Data Scientist | Machine Learning Engineer | PGP in AIML from University of Texas, Great Learning</p>
        </div>
      </header>

      <section className="py-16 bg-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8">About Me</h2>
          <p className="text-gray-700 max-w-3xl mx-auto">
            A passionate data scientist with expertise in machine learning, deep learning, and statistical analysis. 
            Experienced in developing end-to-end solutions across various domains including computer vision, 
            natural language processing, and predictive analytics. Graduate from Texas McCombs School of Business 
            with a proven track record of delivering impactful data-driven solutions.
          </p>
        </div>
      </section>

      <main className="container mx-auto px-4 py-16">
        <section>
          <h2 className="text-3xl font-bold mb-12 text-center">Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {projects.map((project, index) => (
              <a 
                href={project.githubLink}
                target="_blank"
                rel="noopener noreferrer"
                key={index}
                className="block transform hover:-translate-y-1 transition-all duration-300"
              >
                <div className="bg-white rounded-lg shadow-lg p-6 h-full hover:shadow-xl">
                  <h3 className="text-xl font-bold mb-4 text-purple-900">{project.title}</h3>
                  <p className="text-gray-700 mb-4">{project.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {project.skills.map((skill, skillIndex) => (
                      <span 
                        key={skillIndex}
                        className="bg-purple-100 text-purple-900 px-3 py-1 rounded-full text-sm"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </a>
            ))}
          </div>
        </section>
      </main>

      <footer className="bg-purple-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <div className="flex justify-center space-x-6">
            <a href="https://github.com/JannetEkka" className="hover:text-purple-200 transition-colors duration-300">GitHub</a>
            <a href="https://www.linkedin.com/in/jannet-akanksha-ekka-a18692122/" className="hover:text-purple-200 transition-colors duration-300">LinkedIn</a>
            <a href="mailto:jannetekka96@gmail.com" className="hover:text-purple-200 transition-colors duration-300">Email</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PortfolioApp;