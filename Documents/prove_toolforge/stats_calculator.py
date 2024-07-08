import pandas as pd
import re
import html

def stats(entity):
    # Calculate total claims
    li =[]
    total_claims = sum(len(claims) for claims in entity['claims'].values())

    # Calculate claims with references and total references
    ref_claims = 0
    total_refs = 0
    for claims in entity['claims'].values():
        for claim in claims:
            if 'references' in claim:
                ref_claims += 1
                total_refs += len(claim['references'])

    # Calculate total property types
    total_property_types = len(entity['property_info'])

    # Calculate references per property type
    property_ref_counts = {}
    for prop, claims in entity['claims'].items():
        property_ref_counts[prop] = sum(1 for claim in claims if 'references' in claim)

    # Calculate statistics
    ref_claim_ratio = ref_claims / total_claims if total_claims > 0 else 0
    avg_refs_per_ref_claim = total_refs / ref_claims if ref_claims > 0 else 0
    ref_property_types = sum(1 for count in property_ref_counts.values() if count > 0)
    ref_property_type_ratio = ref_property_types / total_property_types if total_property_types > 0 else 0
    avg_ref_claims_per_property = sum(property_ref_counts.values()) / ref_property_types if ref_property_types > 0 else 0

    li.append(f"1. Total number of claims: {total_claims}")
    li.append(f"2. Number of claims with references: {ref_claims}")
    li.append(f"3. Ratio of claims with references to total claims: {ref_claim_ratio:.2%}")
    li.append(f"4. Average number of references per claim with references: {avg_refs_per_ref_claim:.2f}")
    li.append(f"5. Total number of property types: {total_property_types}")
    li.append(f"6. Number of property types with references: {ref_property_types}")
    li.append(f"7. Ratio of property types with references to total property types: {ref_property_type_ratio:.2%}")
    li.append(f"8. Average number of claims with references per property type with reference: {avg_ref_claims_per_property:.2f}")

    return li

def entailmentResult(results):
    result = results.reset_index(drop=True).copy()
    aggregated_ = []
    for idx, row in result.iterrows():
        if 'SUPPORTS' in row['Results']['TextEntailment'].tolist():
            aggregated_.append(f"SUPPORTS, with this sentence: {row['Results'][row['Results']['TextEntailment']=='SUPPORTS']['sentence'].iloc[0]}")
        else: 
            value_counts = row['Results']['TextEntailment'].value_counts()
            most_frequent = value_counts.index[0]
            aggregated_.append(f"{most_frequent}, with this sentence: Empty")
    result = pd.concat([result, pd.DataFrame(aggregated_, columns=['final_result'])], axis=1)[['triple', 'final_result', 'url']]
    li = []
    for i in result['triple'].unique():
        for idx, row in result[result['triple']==i][['final_result','url']].iterrows():
            li.append(f"{i}")
            li.append(f"{row['final_result']}, {row['url']}")
    return li

def format_to_html(data):
    style = """
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h1, h2 { color: #333; }
        .statistics { background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
        th { background-color: #f2f2f2; }
        .support { font-weight: bold; }
        .sentence { font-style: italic; color: #666; display: block; margin-top: 5px; }
        .source { font-size: 0.9em; color: #999; display: block; margin-top: 5px; }
    </style>
    """

    html_content = f"""
    <div class="wikidata-content">
        {style}
        <h1>{data[0]}</h1>
        <h2>Statistics</h2>
        <div class='statistics'>
    """

    for stat in data[1:9]:
        html_content += f"<p>{html.escape(stat)}</p>"
    
    html_content += """
        </div>
        <h2>Detailed Information</h2>
        <table>
                  <th>Property</th>
                <th>Value</th>
                <th>Support</th>
            </tr>
    """

    for i in range(9, len(data), 2):
        if i + 1 < len(data):
            parts = data[i].split(', ', 2)
            if len(parts) == 3:
                _, property, value = parts
            else:
                continue

            support_info = data[i+1].split(', ', 1)
            support = support_info[0]
            
            if len(support_info) > 1:
                if support == "SUPPORTS":
                    sentence, source = support_info[1].rsplit(', http', 1)
                    source = 'http' + source
                else:
                    sentence = support_info[1]
                    source = ""
            else:
                sentence = ""
                source = ""

            html_content += f"""
                <tr>
                    <td>{html.escape(property)}</td>
                    <td>{html.escape(value)}</td>
                    <td>
                        <span class="support">{html.escape(support)}</span>
                        {f'<span class="sentence">{html.escape(sentence)}</span>' if sentence else ''}
                        {f'<span class="source">Source: {html.escape(source)}</span>' if source else ''}
                    </td>
                </tr>
            """

    html_content += """
        </table>
    </div>
    """

    return html_content

if __name__ == '__main__':
    result_values = [entity['label']]
    result_values += stats(entity)
    result_values += entailmentResult(results)
    html_content = format_to_html(result_values)


