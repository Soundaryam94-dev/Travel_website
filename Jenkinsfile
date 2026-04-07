pipeline {
    agent any

    environment {
        VERCEL_TOKEN = credentials('vercel-token')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Soundaryam94-dev/Travel_website.git'
            }
        }

        stage('Deploy to Vercel') {
            steps {
                bat 'npx vercel --prod --yes --token=%VERCEL_TOKEN% --name travel-website'
            }
        }
    }
}
