import csv
import re
from typing import List, Tuple, Dict

class NSFWDetector:
    def __init__(self):
        self.nsfw_keywords = {
            'explicit': [
                'porn', 'xxx', 'sex', 'nude', 'naked', 'nsfw', 'adult', 'milf',
                'boobs', 'ass', 'dick', 'cock', 'pussy', 'tits', 'anal', 'oral',
                'cum', 'orgasm', 'fetish', 'kink', 'bdsm', 'gonewild', 'strip',
                'lesbian', 'gay', 'bisexual', 'transgender', 'erotic', 'hentai',
                'amateur', 'masturbation', 'webcam', 'camgirl', 'escort', 'hookup'
            ],
            'suggestive': [
                'hot', 'sexy', 'wild', 'dirty', 'naughty', 'thick', 'curvy',
                'busty', 'horny', 'kinky', 'slutty', 'daddy', 'mommy', 'breeding',
                'tribute', 'jerk', 'rate', 'college', 'teen', 'barely', 'legal',
                'virgin', 'first', 'real', 'wife', 'gf', 'girlfriend', 'cheating'
            ],
            'body_parts': [
                'booty', 'butt', 'chest', 'cleavage', 'thigh', 'legs', 'feet',
                'abs', 'muscle', 'bikini', 'lingerie', 'underwear', 'panties',
                'bra', 'topless', 'bottomless'
            ],
            'community_indicators': [
                'gone', 'wild', 'rate', 'tribute', 'verification', 'request',
                'personals', 'r4r', 'meetup', 'hookups', 'dirty', 'kik', 'snap'
            ]
        }
        
        # Age-related terms that are often NSFW in context
        self.age_terms = ['18', '19', '20', '21', 'teen', 'college', 'young', 'legal']
        
        # Common NSFW subreddit patterns
        self.nsfw_patterns = [
            r'.*gonewild.*',
            r'.*porn.*',
            r'.*xxx.*',
            r'.*nsfw.*',
            r'.*nude.*',
            r'.*sex.*',
            r'.*adult.*',
            r'.*18.*plus.*',
            r'.*over.*18.*',
            r'.*r4r.*',
            r'.*dirty.*',
            r'.*naughty.*',
            r'.*fetish.*',
            r'.*kink.*',
            r'.*bdsm.*',
            r'.*strip.*',
            r'.*cam.*girl.*',
            r'.*hot.*wife.*',
            r'.*milf.*',
            r'.*tribute.*'
        ]

    def detect_nsfw(self, subreddit_name: str) -> Tuple[bool, str, int]:
        """
        Detect if a subreddit is NSFW based on its name.
        
        Returns:
            Tuple[bool, str, int]: (is_nsfw, reason, confidence_score)
            confidence_score: 1-10 scale (10 = definitely NSFW)
        """
        name_lower = subreddit_name.lower()
        reasons = []
        confidence = 0
        
        # Check explicit patterns first (highest confidence)
        for pattern in self.nsfw_patterns:
            if re.match(pattern, name_lower):
                reasons.append(f"Matches NSFW pattern: {pattern}")
                confidence = max(confidence, 9)
        
        # Check explicit keywords
        for keyword in self.nsfw_keywords['explicit']:
            if keyword in name_lower:
                reasons.append(f"Contains explicit keyword: {keyword}")
                confidence = max(confidence, 8)
        
        # Check suggestive keywords
        suggestive_count = 0
        for keyword in self.nsfw_keywords['suggestive']:
            if keyword in name_lower:
                suggestive_count += 1
                if suggestive_count == 1:
                    reasons.append(f"Contains suggestive keywords")
                confidence = max(confidence, 6)
        
        # Check body parts keywords
        body_count = 0
        for keyword in self.nsfw_keywords['body_parts']:
            if keyword in name_lower:
                body_count += 1
                if body_count == 1:
                    reasons.append(f"Contains body-related keywords")
                confidence = max(confidence, 5)
        
        # Check community indicators
        community_count = 0
        for keyword in self.nsfw_keywords['community_indicators']:
            if keyword in name_lower:
                community_count += 1
                if community_count == 1:
                    reasons.append(f"Contains NSFW community indicators")
                confidence = max(confidence, 4)
        
        # Age-related context (lower confidence, needs other indicators)
        age_found = False
        for term in self.age_terms:
            if term in name_lower:
                age_found = True
                break
        
        if age_found and (suggestive_count > 0 or body_count > 0):
            reasons.append("Age-related terms with suggestive content")
            confidence = max(confidence, 7)
        
        # Combine multiple lower-confidence indicators
        total_indicators = suggestive_count + body_count + community_count
        if total_indicators >= 2:
            confidence = max(confidence, 6)
        
        is_nsfw = confidence >= 5
        reason_text = "; ".join(reasons) if reasons else "No NSFW indicators found"
        
        return is_nsfw, reason_text, confidence

    def process_csv_file(self, input_file: str, output_file: str) -> Dict[str, int]:
        """
        Process the entire CSV file and add NSFW classification.
        
        Returns statistics about the classification.
        """
        stats = {'total': 0, 'nsfw': 0, 'safe': 0, 'high_confidence_nsfw': 0}
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['NSFW_Flag', 'NSFW_Reason', 'Confidence_Score']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                subreddit = row['Subreddit']
                is_nsfw, reason, confidence = self.detect_nsfw(subreddit)
                
                row['NSFW_Flag'] = 'YES' if is_nsfw else 'NO'
                row['NSFW_Reason'] = reason
                row['Confidence_Score'] = confidence
                
                writer.writerow(row)
                
                stats['total'] += 1
                if is_nsfw:
                    stats['nsfw'] += 1
                    if confidence >= 8:
                        stats['high_confidence_nsfw'] += 1
                else:
                    stats['safe'] += 1
        
        return stats

def main():
    detector = NSFWDetector()
    
    input_file = r'C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Subreddits\Reddit SubReddits - ALL SUBREDDITS.csv'
    output_file = r'C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Subreddits\Reddit_SubReddits_NSFW_Classified.csv'
    
    print("Starting NSFW classification of subreddits...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    try:
        stats = detector.process_csv_file(input_file, output_file)
        
        print("Classification completed!")
        print(f"Total subreddits processed: {stats['total']}")
        print(f"NSFW subreddits found: {stats['nsfw']} ({stats['nsfw']/stats['total']*100:.1f}%)")
        print(f"Safe subreddits: {stats['safe']} ({stats['safe']/stats['total']*100:.1f}%)")
        print(f"High confidence NSFW: {stats['high_confidence_nsfw']}")
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()