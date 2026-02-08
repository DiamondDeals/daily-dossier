import csv

def split_nsfw_results(input_file: str):
    """
    Split the NSFW classified results into separate CSV files.
    """
    nsfw_file = input_file.replace('.csv', '_NSFW_ONLY.csv')
    safe_file = input_file.replace('.csv', '_SAFE_ONLY.csv')
    
    nsfw_count = 0
    safe_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Open both output files
        with open(nsfw_file, 'w', newline='', encoding='utf-8') as nsfw_out, \
             open(safe_file, 'w', newline='', encoding='utf-8') as safe_out:
            
            nsfw_writer = csv.DictWriter(nsfw_out, fieldnames=fieldnames)
            safe_writer = csv.DictWriter(safe_out, fieldnames=fieldnames)
            
            # Write headers
            nsfw_writer.writeheader()
            safe_writer.writeheader()
            
            # Process each row
            for row in reader:
                if row['NSFW_Flag'] == 'YES':
                    nsfw_writer.writerow(row)
                    nsfw_count += 1
                else:
                    safe_writer.writerow(row)
                    safe_count += 1
    
    return nsfw_file, safe_file, nsfw_count, safe_count

def main():
    input_file = r'C:\Users\Carzl\Documents\Python Stuff\Pet\Reddit Helper Helper\Subreddits\Reddit_SubReddits_NSFW_Classified.csv'
    
    print("Splitting NSFW classified results into separate files...")
    
    nsfw_file, safe_file, nsfw_count, safe_count = split_nsfw_results(input_file)
    
    print(f"NSFW subreddits ({nsfw_count}) saved to: {nsfw_file}")
    print(f"Safe subreddits ({safe_count}) saved to: {safe_file}")

if __name__ == "__main__":
    main()