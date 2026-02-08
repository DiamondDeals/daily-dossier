#!/usr/bin/env python3
"""
Digest Evaluator - Learn and improve over time
Tracks what works, what doesn't, and adjusts
"""
import json
from datetime import datetime
from pathlib import Path

class DigestEvaluator:
    def __init__(self):
        self.history_file = Path("digest_history.json")
        self.load_history()
    
    def load_history(self):
        """Load evaluation history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {
                "runs": [],
                "learnings": [],
                "improvements": []
            }
    
    def save_history(self):
        """Save evaluation history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def record_run(self, reddit_count, twitter_count, top_scores):
        """Record a digest run"""
        run = {
            "timestamp": datetime.now().isoformat(),
            "reddit_leads": reddit_count,
            "twitter_leads": twitter_count,
            "top_reddit_score": max([s['engagement_score'] for s in top_scores['reddit'][:3]]) if top_scores['reddit'] else 0,
            "top_twitter_score": max([s['total_score'] for s in top_scores['twitter'][:3]]) if top_scores['twitter'] else 0
        }
        
        self.history['runs'].append(run)
        
        # Keep last 30 runs
        if len(self.history['runs']) > 30:
            self.history['runs'] = self.history['runs'][-30:]
        
        self.save_history()
        return run
    
    def evaluate(self):
        """Evaluate performance and generate insights"""
        if len(self.history['runs']) < 2:
            return {"status": "Need more data (minimum 2 runs)"}
        
        runs = self.history['runs']
        recent = runs[-7:]  # Last week
        
        # Calculate averages
        avg_reddit = sum(r['reddit_leads'] for r in recent) / len(recent)
        avg_twitter = sum(r['twitter_leads'] for r in recent) / len(recent)
        
        # Trends
        reddit_trend = "📈 Improving" if recent[-1]['reddit_leads'] > avg_reddit else "📉 Declining"
        twitter_trend = "📈 Improving" if recent[-1]['twitter_leads'] > avg_twitter else "📉 Declining"
        
        # Quality (avg of top scores)
        avg_reddit_quality = sum(r['top_reddit_score'] for r in recent) / len(recent)
        avg_twitter_quality = sum(r['top_twitter_score'] for r in recent) / len(recent)
        
        evaluation = {
            "period": f"Last {len(recent)} runs",
            "reddit": {
                "avg_leads": round(avg_reddit, 1),
                "trend": reddit_trend,
                "avg_quality": round(avg_reddit_quality, 1)
            },
            "twitter": {
                "avg_leads": round(avg_twitter, 1),
                "trend": twitter_trend,
                "avg_quality": round(avg_twitter_quality, 1)
            },
            "insights": self._generate_insights(recent)
        }
        
        return evaluation
    
    def _generate_insights(self, runs):
        """Generate actionable insights"""
        insights = []
        
        # Check if Reddit consistently low
        avg_reddit = sum(r['reddit_leads'] for r in runs) / len(runs)
        if avg_reddit < 10:
            insights.append("⚠️ Low Reddit leads - consider expanding subreddit list")
        
        # Check if Twitter consistently low
        avg_twitter = sum(r['twitter_leads'] for r in runs) / len(runs)
        if avg_twitter < 15:
            insights.append("⚠️ Low Twitter leads - consider increasing account scan count")
        
        # Check quality
        avg_reddit_quality = sum(r['top_reddit_score'] for r in runs) / len(runs)
        if avg_reddit_quality < 100:
            insights.append("💡 Reddit engagement low - focus on more active subreddits")
        
        # Success patterns
        if avg_reddit > 20 and avg_twitter > 20:
            insights.append("✅ Strong performance across both platforms")
        
        return insights if insights else ["✅ Performance within expected range"]
    
    def add_learning(self, learning):
        """Manually add a learning/observation"""
        self.history['learnings'].append({
            "timestamp": datetime.now().isoformat(),
            "learning": learning
        })
        self.save_history()
    
    def add_improvement(self, improvement):
        """Track an improvement made"""
        self.history['improvements'].append({
            "timestamp": datetime.now().isoformat(),
            "improvement": improvement
        })
        self.save_history()
    
    def generate_report(self):
        """Generate evaluation report"""
        eval_data = self.evaluate()
        
        report = []
        report.append("## 📊 Digest Performance Evaluation\n")
        
        if "status" in eval_data:
            report.append(f"*{eval_data['status']}*\n")
        else:
            report.append(f"**Period:** {eval_data['period']}\n")
            
            report.append("### Reddit Performance")
            report.append(f"- Average leads: {eval_data['reddit']['avg_leads']}")
            report.append(f"- Trend: {eval_data['reddit']['trend']}")
            report.append(f"- Avg quality score: {eval_data['reddit']['avg_quality']}\n")
            
            report.append("### Twitter Performance")
            report.append(f"- Average leads: {eval_data['twitter']['avg_leads']}")
            report.append(f"- Trend: {eval_data['twitter']['trend']}")
            report.append(f"- Avg quality score: {eval_data['twitter']['avg_quality']}\n")
            
            report.append("### Insights")
            for insight in eval_data['insights']:
                report.append(f"- {insight}")
        
        # Recent learnings
        if self.history['learnings']:
            report.append("\n### Recent Learnings")
            for learning in self.history['learnings'][-5:]:
                report.append(f"- {learning['learning']}")
        
        # Recent improvements
        if self.history['improvements']:
            report.append("\n### Recent Improvements")
            for improvement in self.history['improvements'][-5:]:
                report.append(f"- {improvement['improvement']}")
        
        return '\n'.join(report)

if __name__ == '__main__':
    print("=" * 70)
    print("DIGEST EVALUATOR - LEARNING & IMPROVEMENT SYSTEM")
    print("=" * 70)
    
    evaluator = DigestEvaluator()
    
    # Example: Record a run
    evaluator.record_run(
        reddit_count=25,
        twitter_count=20,
        top_scores={
            'reddit': [{'engagement_score': 150}, {'engagement_score': 120}],
            'twitter': [{'total_score': 250}, {'total_score': 200}]
        }
    )
    
    # Generate evaluation
    print("\n" + evaluator.generate_report())
    
    print("\n" + "=" * 70)
    print("✅ Evaluation system ready!")
    print("=" * 70)
