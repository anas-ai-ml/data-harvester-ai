import { JobStatus } from "@/components/jobStatus";
import { QueryForm } from "@/components/queryForm";
import { BulkUpload } from "@/components/bulkUpload";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sparkles, Globe2, FileUp, Search } from "lucide-react";

export default function ScraperPage() {
  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <section className="relative">
        <div className="absolute -left-4 top-0 h-12 w-1 rounded-r-full bg-gradient-to-b from-primary to-purple-600 shadow-[0_0_10px_rgba(var(--primary),0.5)]" />
        
        <div className="flex items-center gap-3">
          <Globe2 className="h-5 w-5 text-primary animate-pulse" />
          <p className="text-sm uppercase tracking-[0.2em] font-medium text-primary/80">
            Intelligent Extraction Engine
          </p>
        </div>
        
        <h2 className="mt-3 text-4xl font-black tracking-tight text-white lg:text-5xl">
          Harvest <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400">Global Data</span>
        </h2>
        
        <p className="mt-4 max-w-2xl text-lg text-white/50 leading-relaxed">
          Deploy AI-powered extraction agents to seamlessly gather company profiles, decision-makers, and market intelligence across the web.
        </p>
      </section>

      <div className="grid gap-8 xl:grid-cols-[1.3fr_0.8fr]">
        <div className="space-y-6">
          <Tabs defaultValue="single" className="w-full">
            <TabsList className="grid w-full max-w-[400px] grid-cols-2 bg-black/40 border border-white/10 p-1 rounded-2xl h-12">
              <TabsTrigger value="single" className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-black transition-all">
                <Search className="h-4 w-4 mr-2" />
                Single Search
              </TabsTrigger>
              <TabsTrigger value="bulk" className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-black transition-all">
                <FileUp className="h-4 w-4 mr-2" />
                Bulk Upload
              </TabsTrigger>
            </TabsList>

            <TabsContent value="single" className="mt-6">
              <Card className="relative overflow-hidden bg-black/40 border-white/5 backdrop-blur-xl shadow-2xl">
                <div className="absolute top-0 right-0 p-8 w-64 h-64 bg-primary/10 rounded-full blur-[100px] pointer-events-none" />
                <div className="absolute bottom-0 left-0 p-8 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />
                
                <div className="relative p-6 sm:p-8">
                  <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                      <Sparkles className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">Extraction Parameters</h3>
                      <p className="text-sm text-white/50">Define your target criteria below</p>
                    </div>
                  </div>
                  <QueryForm />
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="bulk" className="mt-6">
              <Card className="relative overflow-hidden bg-black/40 border-white/5 backdrop-blur-xl shadow-2xl">
                <div className="relative p-6 sm:p-8">
                  <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                      <FileUp className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">Bulk Data Import</h3>
                      <p className="text-sm text-white/50">Upload your JSON or CSV parameter file</p>
                    </div>
                  </div>
                  <BulkUpload />
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
        
        <div className="xl:sticky xl:top-24 h-fit">
          <JobStatus />
        </div>
      </div>
    </div>
  );
}
