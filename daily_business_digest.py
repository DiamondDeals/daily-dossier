#!/usr/bin/env python3
"""
Daily Business Intelligence Digest for Drew
Delivers 50 categorized business opportunities from Reddit every day at 5 AM PT

Categories:
1. Direct Money-Making (15 ideas)
2. Blue Ocean Opportunities (10 ideas)
3. Scale-Ready Ideas (10 ideas)
4. B2B Service Needs (10 ideas)
5. Hidden Gems (5 ideas)
"""

import praw
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import re
from collections import defaultdict
import time
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

@dataclass
class BusinessOpportunity:
    """Enhanced post data with business intelligence"""
    id: str
    title: str
    text: str
    author: str
    subreddit: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    age_hours: float
    
    # Business Intelligence
    category: str
    business_score: float
    urgency_level: str  # high, medium, low
    value_signals: List[str]
    problem_indicators: List[str]
    blue_ocean_score: float
    scale_potential: int  # 1-10
    competition_level: str  # low, medium, high
    
    # Why it matters
    opportunity_summary: str
    action_items: List[str]


class BusinessIntelligenceEngine:
    """Advanced categorization and scoring engine"""
    
    def __init__(self):
        self.setup_patterns()
        
    def setup_patterns(self):
        """Define keyword patterns for each category"""
        
        # Category 1: Direct Money-Making
        self.money_making_patterns = {
            'budget_signals': [
                r'\$\d+k?\s*(budget|to\s*spend|available|willing\s*to\s*pay)',
                r'(budget|willing\s*to\s*pay|can\s*pay)\s*\$?\d+',
                r'(paid|paying|compensation)',
            ],
            'revenue_mentions': [
                r'revenue', r'sales', r'profit', r'make\s*money', 
                r'earn', r'income', r'monetize',
            ],
            'business_owner': [
                r'(my|our)\s*(business|company|startup)',
                r'I\s*(own|run|operate)',
                r'business\s*owner',
            ],
        }
        
        # Category 2: Blue Ocean (unsolved, underserved)
        self.blue_ocean_patterns = {
            'unsolved': [
                r'no\s*(good\s*)?(solution|option|tool|way)',
                r'nothing\s*(out\s*there|available|exists)',
                r"can't\s*find\s*(anything|a\s*solution)",
                r'wish\s*(there\s*was|existed)',
            ],
            'frustration': [
                r'frustrated', r'annoying', r'painful', r'terrible',
                r'hate\s*(doing|that)', r'nightmare',
            ],
            'niche': [
                r'specific\s*to', r'unique\s*situation', r'unusual\s*case',
                r'our\s*industry', r'niche',
            ],
        }
        
        # Category 3: Scale-Ready
        self.scale_patterns = {
            'volume': [
                r'hundreds', r'thousands', r'tons\s*of', r'massive',
                r'bulk', r'mass', r'at\s*scale',
            ],
            'automation': [
                r'automat(e|ion)', r'streamline', r'optimize',
                r'workflow', r'process\s*improvement',
            ],
            'productizable': [
                r'tool', r'platform', r'software', r'app', r'service',
                r'API', r'integration',
            ],
        }
        
        # Category 4: B2B Service Needs
        self.b2b_patterns = {
            'professional': [
                r'consultant', r'agency', r'done[-\s]*for[-\s]*you',
                r'professional\s*services', r'expert',
            ],
            'implementation': [
                r'implement', r'set\s*up', r'deploy', r'migrate',
                r'build\s*for\s*me',
            ],
            'ongoing': [
                r'ongoing', r'retainer', r'monthly', r'subscription',
                r'long[-\s]*term',
            ],
        }
        
        # Urgency indicators
        self.urgency_high = [
            r'urgent', r'asap', r'immediately', r'right\s*now',
            r'today', r'crisis', r'emergency',
        ]
        
        self.urgency_medium = [
            r'soon', r'this\s*week', r'this\s*month', r'deadline',
            r'time[-\s]*sensitive',
        ]
        
        # Value signals
        self.value_signals = {
            'high': [
                r'\$\d{4,}', r'enterprise', r'scale', r'growing\s*fast',
            ],
            'decision_maker': [
                r'(my|our)\s*(company|business)', r'I\s*(own|run)',
                r'CEO', r'founder', r'decision\s*maker',
            ],
        }
        
    def categorize_post(self, post) -> Tuple[str, float, Dict]:
        """Determine best category and score for a post"""
        text = f"{post.title} {post.selftext}".lower()
        
        # Score each category
        scores = {
            'money_making': self._score_money_making(text),
            'blue_ocean': self._score_blue_ocean(text),
            'scale_ready': self._score_scale_ready(text),
            'b2b_service': self._score_b2b_service(text),
            'hidden_gem': self._score_hidden_gem(post),
        }
        
        # Additional metadata
        metadata = {
            'urgency': self._detect_urgency(text),
            'value_signals': self._detect_value_signals(text),
            'problem_indicators': self._detect_problems(text),
            'blue_ocean_score': scores['blue_ocean'],
            'scale_potential': self._assess_scale_potential(text),
            'competition_level': self._assess_competition(post),
        }
        
        # Best category
        best_category = max(scores.items(), key=lambda x: x[1])
        
        return best_category[0], best_category[1], metadata
        
    def _score_money_making(self, text: str) -> float:
        """Score for direct money-making potential"""
        score = 0.0
        
        # Budget signals (high value)
        for pattern in self.money_making_patterns['budget_signals']:
            if re.search(pattern, text, re.I):
                score += 3.0
                
        # Revenue mentions
        for pattern in self.money_making_patterns['revenue_mentions']:
            if re.search(pattern, text, re.I):
                score += 1.5
                
        # Business owner signals
        for pattern in self.money_making_patterns['business_owner']:
            if re.search(pattern, text, re.I):
                score += 2.0
                
        return min(score, 10.0)
        
    def _score_blue_ocean(self, text: str) -> float:
        """Score for blue ocean opportunity"""
        score = 0.0
        
        # Unsolved problem signals (very high value)
        for pattern in self.blue_ocean_patterns['unsolved']:
            if re.search(pattern, text, re.I):
                score += 4.0
                
        # Frustration indicators
        for pattern in self.blue_ocean_patterns['frustration']:
            if re.search(pattern, text, re.I):
                score += 2.0
                
        # Niche/specific situation
        for pattern in self.blue_ocean_patterns['niche']:
            if re.search(pattern, text, re.I):
                score += 2.5
                
        return min(score, 10.0)
        
    def _score_scale_ready(self, text: str) -> float:
        """Score for scalability/productization potential"""
        score = 0.0
        
        # Volume indicators
        for pattern in self.scale_patterns['volume']:
            if re.search(pattern, text, re.I):
                score += 2.5
                
        # Automation mentions
        for pattern in self.scale_patterns['automation']:
            if re.search(pattern, text, re.I):
                score += 3.0
                
        # Productizable signals
        for pattern in self.scale_patterns['productizable']:
            if re.search(pattern, text, re.I):
                score += 2.0
                
        return min(score, 10.0)
        
    def _score_b2b_service(self, text: str) -> float:
        """Score for B2B service opportunity"""
        score = 0.0
        
        # Professional service needs
        for pattern in self.b2b_patterns['professional']:
            if re.search(pattern, text, re.I):
                score += 2.5
                
        # Implementation needs
        for pattern in self.b2b_patterns['implementation']:
            if re.search(pattern, text, re.I):
                score += 2.0
                
        # Ongoing relationship signals
        for pattern in self.b2b_patterns['ongoing']:
            if re.search(pattern, text, re.I):
                score += 3.0
                
        return min(score, 10.0)
        
    def _score_hidden_gem(self, post) -> float:
        """Score based on engagement and subreddit size"""
        score = 0.0
        
        # Good engagement but not too much competition
        if 10 <= post.score <= 100:
            score += 3.0
        elif 5 <= post.score < 10:
            score += 2.0
            
        # Active discussion
        if 5 <= post.num_comments <= 50:
            score += 2.0
            
        # Fresh post (< 24 hours)
        age_hours = (datetime.utcnow().timestamp() - post.created_utc) / 3600
        if age_hours < 24:
            score += 3.0
        elif age_hours < 48:
            score += 1.5
            
        return min(score, 10.0)
        
    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level"""
        for pattern in self.urgency_high:
            if re.search(pattern, text, re.I):
                return 'high'
                
        for pattern in self.urgency_medium:
            if re.search(pattern, text, re.I):
                return 'medium'
                
        return 'low'
        
    def _detect_value_signals(self, text: str) -> List[str]:
        """Detect value indicators"""
        signals = []
        
        for category, patterns in self.value_signals.items():
            for pattern in patterns:
                if re.search(pattern, text, re.I):
                    signals.append(category)
                    break
                    
        # Extract budget amounts
        budget_match = re.search(r'\$\d+[,\d]*k?', text, re.I)
        if budget_match:
            signals.append(f"budget: {budget_match.group()}")
            
        return signals
        
    def _detect_problems(self, text: str) -> List[str]:
        """Detect problem indicators"""
        problems = []
        
        problem_keywords = [
            'manual', 'tedious', 'time-consuming', 'repetitive',
            'bottleneck', 'inefficient', 'struggling', 'difficult',
            'problem', 'issue', 'challenge', 'pain point',
        ]
        
        for keyword in problem_keywords:
            if keyword in text:
                problems.append(keyword)
                
        return problems[:5]  # Top 5
        
    def _assess_scale_potential(self, text: str) -> int:
        """Assess scalability (1-10)"""
        scale_score = 5  # baseline
        
        # Positive indicators
        if re.search(r'(multiple|many|several)\s*(clients|customers|businesses)', text, re.I):
            scale_score += 2
        if re.search(r'(saas|software|platform|api)', text, re.I):
            scale_score += 2
        if re.search(r'(recurring|subscription|monthly)', text, re.I):
            scale_score += 1
            
        return min(scale_score, 10)
        
    def _assess_competition(self, post) -> str:
        """Estimate competition level"""
        # Simple heuristic based on subreddit size and comment engagement
        if post.num_comments > 50:
            return 'high'
        elif post.num_comments > 20:
            return 'medium'
        else:
            return 'low'


class DailyDigestBot:
    """Main automation bot"""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.db_path = workspace_dir / "digest_history.db"
        self.config_path = workspace_dir / "digest_config.json"
        
        self.intelligence = BusinessIntelligenceEngine()
        self.reddit = None
        
        self.setup_database()
        self.load_config()
        
    def setup_database(self):
        """Initialize SQLite database for tracking sent posts"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS sent_posts (
                post_id TEXT PRIMARY KEY,
                title TEXT,
                subreddit TEXT,
                category TEXT,
                score REAL,
                sent_date TEXT,
                user_feedback TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS digest_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT,
                posts_analyzed INTEGER,
                posts_sent INTEGER,
                categories_breakdown TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_config(self):
        """Load configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            # Default config
            self.config = {
                'target_subreddits': [
                    # High-value B2B
                    'entrepreneur', 'smallbusiness', 'Accounting', 'realestate',
                    'sweatystartup', 'ecommerce', 'startups',
                    # Service business
                    'restaurateur', 'freelance', 'consulting', 'digitalmarketing',
                    'marketing', 'sales', 'business',
                    # Niche opportunities
                    'sysadmin', 'excel', 'productivity', 'workflow',
                    'automation', 'process', 'operations',
                    # Money-making
                    'passive_income', 'sidehustle', 'Flipping', 'investing',
                    'realestateinvesting', 'entrepreneurridealong',
                ],
                'min_score': 5,
                'max_post_age_hours': 48,
                'categories_quota': {
                    'money_making': 15,
                    'blue_ocean': 10,
                    'scale_ready': 10,
                    'b2b_service': 10,
                    'hidden_gem': 5,
                },
            }
            self.save_config()
            
    def save_config(self):
        """Save configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def authenticate(self, client_id: str, client_secret: str, user_agent: str,
                     username: str = None, password: str = None):
        """Authenticate with Reddit API"""
        try:
            if username and password:
                # Script app (username/password)
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                    username=username,
                    password=password,
                )
            else:
                # Read-only mode (no authentication required for reading public posts)
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                )
                
            # Test authentication
            if username:
                me = self.reddit.user.me()
                print(f"✓ Authenticated as: {me.name}")
            else:
                print("✓ Connected in read-only mode")
                
            return True
            
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
            
    def is_duplicate(self, post_id: str) -> bool:
        """Check if post was already sent"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT 1 FROM sent_posts WHERE post_id = ?', (post_id,))
        result = c.fetchone()
        conn.close()
        return result is not None
        
    def mark_as_sent(self, opportunity: BusinessOpportunity):
        """Mark post as sent"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO sent_posts 
            (post_id, title, subreddit, category, score, sent_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            opportunity.id,
            opportunity.title,
            opportunity.subreddit,
            opportunity.category,
            opportunity.business_score,
            datetime.now().isoformat(),
        ))
        conn.commit()
        conn.close()
        
    def fetch_opportunities(self) -> List[BusinessOpportunity]:
        """Fetch and analyze posts from target subreddits"""
        if not self.reddit:
            raise Exception("Not authenticated. Call authenticate() first.")
            
        opportunities = []
        cutoff_time = datetime.utcnow().timestamp() - (self.config['max_post_age_hours'] * 3600)
        
        print(f"📡 Scanning {len(self.config['target_subreddits'])} subreddits...")
        
        for subreddit_name in self.config['target_subreddits']:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get hot and new posts
                posts = list(subreddit.hot(limit=50)) + list(subreddit.new(limit=50))
                
                for post in posts:
                    # Skip if already sent
                    if self.is_duplicate(post.id):
                        continue
                        
                    # Skip if too old
                    if post.created_utc < cutoff_time:
                        continue
                        
                    # Skip if score too low
                    if post.score < self.config['min_score']:
                        continue
                        
                    # Skip if locked/archived
                    if post.locked or post.archived or post.stickied:
                        continue
                        
                    # Categorize and score
                    category, score, metadata = self.intelligence.categorize_post(post)
                    
                    # Only keep if scored well
                    if score >= 5.0:
                        age_hours = (datetime.utcnow().timestamp() - post.created_utc) / 3600
                        
                        # Create opportunity
                        opp = BusinessOpportunity(
                            id=post.id,
                            title=post.title,
                            text=post.selftext[:500] if post.selftext else "",
                            author=str(post.author),
                            subreddit=subreddit_name,
                            url=f"https://reddit.com{post.permalink}",
                            score=post.score,
                            num_comments=post.num_comments,
                            created_utc=post.created_utc,
                            age_hours=age_hours,
                            category=category,
                            business_score=score,
                            urgency_level=metadata['urgency'],
                            value_signals=metadata['value_signals'],
                            problem_indicators=metadata['problem_indicators'],
                            blue_ocean_score=metadata['blue_ocean_score'],
                            scale_potential=metadata['scale_potential'],
                            competition_level=metadata['competition_level'],
                            opportunity_summary=self._generate_summary(post, metadata),
                            action_items=self._generate_action_items(post, metadata),
                        )
                        
                        opportunities.append(opp)
                        
                print(f"  ✓ r/{subreddit_name}: {len([o for o in opportunities if o.subreddit == subreddit_name])} opportunities")
                        
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"  ✗ r/{subreddit_name}: {e}")
                continue
                
        return opportunities
        
    def _generate_summary(self, post, metadata) -> str:
        """Generate opportunity summary"""
        summaries = []
        
        if metadata['urgency'] == 'high':
            summaries.append("🚨 High urgency - immediate need")
        elif metadata['urgency'] == 'medium':
            summaries.append("⚡ Time-sensitive opportunity")
            
        if metadata['blue_ocean_score'] >= 7.0:
            summaries.append("🌊 Blue ocean - limited solutions available")
            
        if metadata['scale_potential'] >= 8:
            summaries.append("📈 High scalability potential")
            
        if metadata['value_signals']:
            summaries.append(f"💰 Value signals: {', '.join(metadata['value_signals'][:2])}")
            
        if not summaries:
            summaries.append("Business opportunity identified")
            
        return " | ".join(summaries)
        
    def _generate_action_items(self, post, metadata) -> List[str]:
        """Generate suggested action items"""
        actions = []
        
        if metadata['urgency'] == 'high':
            actions.append("Respond within 24 hours")
        else:
            actions.append("Review and engage if relevant")
            
        if post.num_comments < 10:
            actions.append("Early mover advantage - low competition")
        else:
            actions.append("Active discussion - multiple perspectives available")
            
        if metadata['blue_ocean_score'] >= 7.0:
            actions.append("Consider productizing the solution")
            
        return actions
        
    def select_top_opportunities(self, opportunities: List[BusinessOpportunity]) -> Dict[str, List[BusinessOpportunity]]:
        """Select top 50 opportunities across categories"""
        
        # Group by category
        by_category = defaultdict(list)
        for opp in opportunities:
            by_category[opp.category].append(opp)
            
        # Sort each category by score
        for category in by_category:
            by_category[category].sort(key=lambda x: x.business_score, reverse=True)
            
        # Select according to quota
        selected = {}
        for category, quota in self.config['categories_quota'].items():
            selected[category] = by_category[category][:quota]
            
        return selected
        
    def format_slack_message(self, selected: Dict[str, List[BusinessOpportunity]]) -> str:
        """Format digest as Slack message"""
        
        total = sum(len(opps) for opps in selected.values())
        
        message = f"""🧠 *Daily Business Intelligence Digest* - {datetime.now().strftime('%B %d, %Y')}

Found *{total} high-value opportunities* today across {len(selected)} categories:

"""
        
        category_names = {
            'money_making': '💰 Direct Money-Making',
            'blue_ocean': '🌊 Blue Ocean Opportunities',
            'scale_ready': '🚀 Scale-Ready Ideas',
            'b2b_service': '🏢 B2B Service Needs',
            'hidden_gem': '💎 Hidden Gems',
        }
        
        category_descriptions = {
            'money_making': 'Business owners with budget looking for solutions',
            'blue_ocean': 'Unsolved problems with limited competition',
            'scale_ready': 'Automation and productization opportunities',
            'b2b_service': 'Professional service and consulting needs',
            'hidden_gem': 'Early-stage opportunities in niche communities',
        }
        
        for category in ['money_making', 'blue_ocean', 'scale_ready', 'b2b_service', 'hidden_gem']:
            opportunities = selected.get(category, [])
            
            if not opportunities:
                continue
                
            message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*{category_names[category]}* ({len(opportunities)} ideas)
_{category_descriptions[category]}_

"""
            
            for i, opp in enumerate(opportunities, 1):
                urgency_emoji = {'high': '🔥', 'medium': '⚡', 'low': '💡'}[opp.urgency_level]
                
                message += f"""
{i}. {urgency_emoji} *{opp.title[:100]}{'...' if len(opp.title) > 100 else ''}*
    r/{opp.subreddit} | {opp.score}↑ {opp.num_comments}💬 | {int(opp.age_hours)}h ago
    
    📊 Score: {opp.business_score:.1f}/10 | Urgency: {opp.urgency_level.upper()}
    
    {opp.opportunity_summary}
    
    🎯 Action: {' | '.join(opp.action_items)}
    
    🔗 <{opp.url}|View on Reddit>

"""
        
        # Add stats footer
        message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *Today's Analytics*
• {total} opportunities identified from {len(self.config['target_subreddits'])} subreddits
• Avg business score: {sum(opp.business_score for cat in selected.values() for opp in cat) / max(total, 1):.1f}/10
• High urgency items: {sum(1 for cat in selected.values() for opp in cat if opp.urgency_level == 'high')}
• Blue ocean scores ≥ 8: {sum(1 for cat in selected.values() for opp in cat if opp.blue_ocean_score >= 8.0)}

💬 *Feedback*: React with 👍 for valuable leads, 👎 to tune filters
⚙️ *Powered by Bishop's Reddit Intelligence Engine*
"""
        
        return message
        
    def run_digest(self) -> str:
        """Run full digest generation"""
        print("\n🚀 Starting Daily Business Digest Generation...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Fetch opportunities
        opportunities = self.fetch_opportunities()
        print(f"\n📊 Total opportunities found: {len(opportunities)}")
        
        if not opportunities:
            return "No new opportunities found today. Try adjusting filters or adding more subreddits."
            
        # Select top across categories
        selected = self.select_top_opportunities(opportunities)
        
        # Mark as sent
        for category_opps in selected.values():
            for opp in category_opps:
                self.mark_as_sent(opp)
                
        # Log run
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO digest_runs (run_date, posts_analyzed, posts_sent, categories_breakdown)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            len(opportunities),
            sum(len(opps) for opps in selected.values()),
            json.dumps({k: len(v) for k, v in selected.items()}),
        ))
        conn.commit()
        conn.close()
        
        # Format message
        message = self.format_slack_message(selected)
        
        print("\n✅ Digest generated successfully!")
        return message


def main():
    """Main entry point"""
    
    # Configuration
    workspace = Path(__file__).parent
    
    # Initialize bot
    bot = DailyDigestBot(workspace)
    
    # Get credentials from environment or .env file
    from dotenv import load_dotenv
    load_dotenv(workspace / '.env')
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'BishopDigestBot/1.0')
    username = os.getenv('REDDIT_USERNAME')
    password = os.getenv('REDDIT_PASSWORD')
    
    if not client_id or not client_secret:
        print("❌ Error: Reddit credentials not found!")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file")
        sys.exit(1)
        
    # Authenticate
    if not bot.authenticate(client_id, client_secret, user_agent, username, password):
        print("❌ Authentication failed")
        sys.exit(1)
        
    # Run digest
    message = bot.run_digest()
    
    # Save to file for review
    output_file = workspace / f"digest_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(message)
        
    print(f"\n💾 Digest saved to: {output_file}")
    print("\n" + "="*60)
    print("PREVIEW:")
    print("="*60)
    print(message[:2000])  # Preview first 2000 chars
    print("\n[... message continues ...]")
    

if __name__ == '__main__':
    main()
