import { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, BarChart3, TrendingUp, CheckCircle2, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import { Toaster } from '@/components/ui/sonner';

const EvaluationPage = () => {
  const [loading, setLoading] = useState(false);
  const [evaluationData, setEvaluationData] = useState(null);
  const [assessmentsCount, setAssessmentsCount] = useState(0);

  useEffect(() => {
    fetchAssessmentsCount();
  }, []);

  const fetchAssessmentsCount = async () => {
    try {
      const response = await axios.get(`${API}/assessments`);
      setAssessmentsCount(response.data.count);
    } catch (error) {
      console.error('Error fetching assessments count:', error);
    }
  };

  const handleScrape = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/scrape`);
      toast.success(response.data.message);
      
      // Wait and refresh count
      setTimeout(() => {
        fetchAssessmentsCount();
      }, 3000);
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to start scraping');
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/evaluate`, {});
      setEvaluationData(response.data);
      toast.success('Evaluation completed successfully');
    } catch (error) {
      console.error('Error:', error);
      toast.error('Evaluation failed. Make sure test data is available.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <a href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-5 h-5" />
                <span className="text-sm font-medium">Back</span>
              </a>
              <div className="h-6 w-px bg-gray-300"></div>
              <h1 className="text-xl font-bold text-gray-900">Evaluation Dashboard</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          {/* Stats Cards */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <Card className="border-2 border-blue-100 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  Catalog Status
                </CardTitle>
                <CardDescription>SHL Assessment Database</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold text-blue-600 mb-4">
                  {assessmentsCount}
                </div>
                <p className="text-sm text-gray-600 mb-4">Assessments indexed</p>
                <Button
                  onClick={handleScrape}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Scraping...
                    </>
                  ) : (
                    'Scrape & Index Assessments'
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card className="border-2 border-purple-100 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  System Evaluation
                </CardTitle>
                <CardDescription>Mean Recall@K Metrics</CardDescription>
              </CardHeader>
              <CardContent>
                {evaluationData ? (
                  <div>
                    <div className="text-4xl font-bold text-purple-600 mb-4">
                      {(evaluationData.mean_recall_at_10 * 100).toFixed(1)}%
                    </div>
                    <p className="text-sm text-gray-600 mb-4">Mean Recall@10</p>
                    <Button
                      onClick={handleEvaluate}
                      disabled={loading}
                      variant="outline"
                      className="w-full"
                    >
                      Re-run Evaluation
                    </Button>
                  </div>
                ) : (
                  <div>
                    <div className="text-4xl font-bold text-gray-400 mb-4">--</div>
                    <p className="text-sm text-gray-600 mb-4">No evaluation data</p>
                    <Button
                      onClick={handleEvaluate}
                      disabled={loading}
                      className="w-full bg-purple-600 hover:bg-purple-700"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Evaluating...
                        </>
                      ) : (
                        'Run Evaluation'
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Evaluation Results */}
          {evaluationData && (
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                  Evaluation Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Metrics Grid */}
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Mean Recall@5</div>
                      <div className="text-3xl font-bold text-blue-700">
                        {(evaluationData.mean_recall_at_5 * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Mean Recall@10</div>
                      <div className="text-3xl font-bold text-purple-700">
                        {(evaluationData.mean_recall_at_10 * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Test Queries</div>
                      <div className="text-3xl font-bold text-green-700">
                        {evaluationData.total_queries}
                      </div>
                    </div>
                  </div>

                  {/* Message */}
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-800">
                      <CheckCircle2 className="w-4 h-4 inline mr-2" />
                      {evaluationData.message}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Info Section */}
          <Card className="mt-8 border-l-4 border-l-blue-600">
            <CardHeader>
              <CardTitle className="text-lg">About Evaluation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-gray-600">
              <p><strong>Mean Recall@K:</strong> Measures how many relevant assessments are retrieved in the top K recommendations.</p>
              <p><strong>Formula:</strong> (Number of relevant items in top K) / (Total relevant items for query)</p>
              <p><strong>Data Pipeline:</strong> Web scraping → Embedding generation → Vector storage → RAG retrieval</p>
              <p><strong>Technology Stack:</strong> FastAPI + Gemini 2.5 Flash + ChromaDB + React</p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default EvaluationPage;
