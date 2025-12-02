import pandas as pd

def convert_ratio_to_watts(CAPACITY_WATTS):
   
    input_file = 'cella_pdu6_hourly.csv'
    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file)


   
    df['actual_power_watts'] = df['measured_power_util'] * CAPACITY_WATTS
    df['actual_prod_power_watts'] = df['production_power_util'] * CAPACITY_WATTS

    # 4. Save the new file with Watts
    output_file = 'cella_pdu6_hourly_watts.csv'
    df.to_csv(output_file, index=False)
    
    # 5. Show a preview
    print("-" * 30)
    print(f"CONVERSION COMPLETE (Capacity: {CAPACITY_WATTS} W)")
    print(f"Saved to: {output_file}")
    print("-" * 30)
    print(df[['timestamp', 'measured_power_util', 'actual_power_watts']].head())

if __name__ == "__main__":
    convert_ratio_to_watts