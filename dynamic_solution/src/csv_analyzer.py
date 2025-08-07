import pandas as pd
import numpy as np
import sys
from collections import Counter
import argparse

def analyze_csv_similarity(file1_path, file2_path):
    """
    Analyze the similarity between two CSV files across multiple dimensions.
    
    Args:
        file1_path (str): Path to first CSV file
        file2_path (str): Path to second CSV file
        
    Returns:
        dict: Similarity scores and details
    """
    # Load CSV files
    try:
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return None
    
    print(f"\n{'='*50}")
    print(f"CSV SIMILARITY ANALYSIS")
    print(f"{'='*50}")
    print(f"Comparing: {file1_path} and {file2_path}\n")
    
    # 1. STRUCTURE ANALYSIS
    print("\n1. STRUCTURE ANALYSIS")
    
    row_count1 = len(df1)
    row_count2 = len(df2)
    col_count1 = len(df1.columns)
    col_count2 = len(df2.columns)
    
    print(f"Row counts: {file1_path} ({row_count1}) vs {file2_path} ({row_count2})")
    print(f"Column counts: {file1_path} ({col_count1}) vs {file2_path} ({col_count2})")
    
    # Calculate structure similarity
    row_count_similarity = (min(row_count1, row_count2) / max(row_count1, row_count2)) * 100
    col_count_similarity = (min(col_count1, col_count2) / max(col_count1, col_count2)) * 100
    structure_similarity = (row_count_similarity + col_count_similarity) / 2
    
    print(f"Row count similarity: {row_count_similarity:.2f}%")
    print(f"Column count similarity: {col_count_similarity:.2f}%")
    print(f"Overall structure similarity: {structure_similarity:.2f}%")
    
    # 2. SCHEMA ANALYSIS
    print("\n2. SCHEMA ANALYSIS")
    
    headers1 = list(df1.columns)
    headers2 = list(df2.columns)
    
    print(f"Headers in {file1_path}:", headers1)
    print(f"Headers in {file2_path}:", headers2)
    
    # Check for common column names
    common_headers = [h for h in headers1 if h in headers2]
    header_similarity = (len(common_headers) / max(len(headers1), len(headers2))) * 100
    
    print(f"Common column names: {len(common_headers)} out of {max(len(headers1), len(headers2))}")
    print(f"Column name similarity: {header_similarity:.2f}%")
    
    # Check column order
    same_order = True
    for i in range(min(len(headers1), len(headers2))):
        if i < len(headers1) and i < len(headers2) and headers1[i] != headers2[i]:
            same_order = False
            break
            
    print(f"Same column order: {same_order}")
    
    if not same_order and common_headers:
        print("Column order comparison:")
        for header in common_headers:
            pos1 = headers1.index(header)
            pos2 = headers2.index(header)
            print(f"  - {header}: position {pos1} in {file1_path}, position {pos2} in {file2_path}")
    
    # 3. DATA DISTRIBUTION ANALYSIS
    print("\n3. DATA DISTRIBUTION ANALYSIS")
    
    distribution_similarities = {}
    
    for header in common_headers:
        print(f"\nAnalyzing column: '{header}'")
        
        # Get values from both dataframes for this column
        if header == "year":
            # First fill NA values, then convert to int, then to string
            values1 = df1[header].fillna(0).astype(int).astype(str).replace('0', '').tolist()
            values2 = df2[header].fillna(0).astype(int).astype(str).replace('0', '').tolist()
        elif header == "sex":
            #Remove the last letter from df1, then turn into list
            values1 = df1[header].astype(str).str[:-1].str.lower().tolist()
            values2 = df2[header].astype(str).str.lower().tolist()
        else:
            #Turn df1 and df2 into lists
            values1 = df1[header].astype(str).str.lower().tolist()
            values2 = df2[header].astype(str).str.lower().tolist()
                
        # Count value frequencies
        counter1 = Counter(values1)
        counter2 = Counter(values2)
        
        # Show top values
        top_values1 = counter1.most_common(3)
        top_values2 = counter2.most_common(3)
        
        print(f"  Top values in {file1_path}:", ", ".join([f"{v} ({c})" for v, c in top_values1]))
        print(f"  Top values in {file2_path}:", ", ".join([f"{v} ({c})" for v, c in top_values2]))
        
        # Calculate distribution similarity using Jaccard similarity on value counts
        all_values = set(counter1.keys()) | set(counter2.keys())
        intersection_sum = sum(min(counter1.get(val, 0), counter2.get(val, 0)) for val in all_values)
        union_sum = sum(counter1.values()) + sum(counter2.values()) - intersection_sum if all_values else 0
        
        # Avoid division by zero
        if union_sum > 0:
            jaccard_similarity = (intersection_sum / union_sum) * 100
        else:
            jaccard_similarity = 0
            
        distribution_similarities[header] = jaccard_similarity
        print(f"  Distribution similarity: {jaccard_similarity:.2f}%")
        
        # Alternative metrics
        # Calculate value set overlap
        unique_values1 = set(values1)
        unique_values2 = set(values2)
        value_overlap = len(unique_values1 & unique_values2) / len(unique_values1 | unique_values2) * 100
        print(f"  Unique value set overlap: {value_overlap:.2f}%")
    
    # Calculate average distribution similarity
    avg_distribution_similarity = (
        sum(distribution_similarities.values()) / len(distribution_similarities)
        if distribution_similarities else 0
    )
    
    print(f"\nAverage distribution similarity across all columns: {avg_distribution_similarity:.2f}%")
    
    # 4. CALCULATE OVERALL SIMILARITY SCORE
    print("\n4. OVERALL SIMILARITY SCORE")
    
    # Define weights for different aspects
    weights = {
        'structure': 0.15,  # Structure (row/column counts)
        'schema': 0.15,     # Schema (column names and order)
        'distribution': 0.7 # Value distributions
    }
    
    # Calculate component scores
    structure_score = structure_similarity
    schema_score = header_similarity
    distribution_score = avg_distribution_similarity
    
    # Calculate final weighted score
    final_similarity_score = (
        (structure_score * weights['structure']) +
        (schema_score * weights['schema']) +
        (distribution_score * weights['distribution'])
    )
    
    print(f"Structure similarity: {structure_score:.2f}% (weight: {weights['structure']})")
    print(f"Schema similarity: {schema_score:.2f}% (weight: {weights['schema']})")
    print(f"Distribution similarity: {distribution_score:.2f}% (weight: {weights['distribution']})")
    
    print(f"\nFINAL SIMILARITY SCORE: {final_similarity_score:.2f}%")
    
    # Return results as a dictionary
    results = {
        'final_score': final_similarity_score,
        'component_scores': {
            'structure': structure_score,
            'schema': schema_score,
            'distribution': distribution_score
        },
        'details': {
            'row_count1': row_count1,
            'row_count2': row_count2,
            'col_count1': col_count1,
            'col_count2': col_count2,
            'common_headers': common_headers,
            'distribution_similarities': distribution_similarities
        }
    }
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Analyze similarity between two CSV files')
    parser.add_argument('file1', help='Path to the first CSV file')
    parser.add_argument('file2', help='Path to the second CSV file')
    args = parser.parse_args()
    
    analyze_csv_similarity(args.file1, args.file2)

if __name__ == "__main__":
    main()