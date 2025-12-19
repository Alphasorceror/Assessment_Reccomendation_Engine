import { useState } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Search, Sparkles, Clock, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';
import { Toaster } from '@/components/ui/sonner';

const HomePage = () => {
  const [query, setQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query or job description');
      return;
    }

    setLoading(true);
    setSearched(true);

    try {
      const response = await axios.post(`${API}/recommend`, { query });
      setRecommendations(response.data.recommended_assessments);
      toast.success(`Found ${response.data.recommended_assessments.length} relevant assessments`);
    } catch (error) {
      console.error('Error:', error);
      toast.error(error.response?.data?.detail || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const sampleQueries = [
    'I am hiring for Java developers who can also collaborate effectively with my business teams.',
    'Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript.',
    'I am hiring for an analyst and want to screen using Cognitive and personality tests.'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900" data-testid="main-heading">SHL Assessment Recommender</h1>
                <p className="text-xs text-gray-500">AI-Powered Assessment Discovery</p>
              </div>
            </div>
            <a href="/evaluation" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              Evaluation Dashboard
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {/* Search Section */}
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-gray-900 mb-3" data-testid="search-section-title">
              Find the Perfect Assessment
            </h2>
            <p className="text-lg text-gray-600">
              Describe your role or paste a job description to get intelligent assessment recommendations
            </p>
          </div>

          {/* Search Card */}
          <Card className="shadow-lg border-0 mb-8">
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="relative">
                  <Textarea
                    data-testid="query-input"
                    placeholder="Enter job description or query here...\n\nExample: I need a Java developer with strong collaboration skills for a mid-level position."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="min-h-[150px] text-base resize-none border-2 focus:border-blue-500 transition-colors"
                  />
                </div>
                
                <Button
                  data-testid="search-button"
                  onClick={handleSearch}
                  disabled={loading}
                  className="w-full h-12 text-base font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-5 w-5" />
                      Get Recommendations
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Sample Queries */}
          {!searched && (
            <div className="mb-12">
              <p className="text-sm font-medium text-gray-700 mb-3">Try these examples:</p>
              <div className="space-y-2">
                {sampleQueries.map((sample, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuery(sample)}
                    className="w-full text-left p-3 rounded-lg bg-white border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all text-sm text-gray-700"
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Results */}
          {searched && !loading && (
            <div className="mt-12">
              <h3 className="text-2xl font-bold text-gray-900 mb-6" data-testid="results-heading">
                Recommended Assessments ({recommendations.length})
              </h3>
              
              {recommendations.length === 0 ? (
                <Card className="p-12 text-center">
                  <p className="text-gray-500">No assessments found. Try a different query.</p>
                </Card>
              ) : (
                <div className="grid gap-6">
                  {recommendations.map((assessment, idx) => (
                    <Card key={idx} className="hover:shadow-xl transition-shadow duration-300" data-testid={`assessment-card-${idx}`}>
                      <CardHeader>
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <CardTitle className="text-xl mb-2" data-testid={`assessment-name-${idx}`}>
                              {assessment.name}
                            </CardTitle>
                            <div className="flex flex-wrap gap-2 mb-3">
                              {assessment.test_type.map((type, typeIdx) => (
                                <Badge key={typeIdx} variant="secondary" className="text-xs">
                                  {type}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <Clock className="w-4 h-4" />
                            <span>{assessment.duration} min</span>
                          </div>
                        </div>
                        <CardDescription className="text-base leading-relaxed" data-testid={`assessment-description-${idx}`}>
                          {assessment.description}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center justify-between">
                          <div className="flex gap-4 text-sm">
                            <span className="text-gray-600">
                              Adaptive: <span className="font-medium">{assessment.adaptive_support}</span>
                            </span>
                            <span className="text-gray-600">
                              Remote: <span className="font-medium">{assessment.remote_support}</span>
                            </span>
                          </div>
                          <Button
                            data-testid={`view-assessment-${idx}`}
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(assessment.url, '_blank')}
                            className="gap-2"
                          >
                            View Assessment
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-md mt-20">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>© 2025 SHL Assessment Recommendation System | Powered by Gemini 2.5 Flash & RAG</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
