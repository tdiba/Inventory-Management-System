#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[3]:


#loading the data
import pandas as pd

inventory_df = pd.read_excel(r"C:\Users\USER\Documents\Chat GPT Projects\RAW DATA\Inventory Management System\inventory_data.xlsx")
supplier_df = pd.read_excel(r"C:\Users\USER\Documents\Chat GPT Projects\RAW DATA\Inventory Management System\supplier_data.xlsx")
restock_df = pd.read_excel(r"C:\Users\USER\Documents\Chat GPT Projects\RAW DATA\Inventory Management System\restock_data.xlsx")

# Displaying the first few rows of each dataframe to verify the data
inventory_df.head(), supplier_df.head(), restock_df.head()


# In[4]:


# Analyzing current inventory levels to categorize items based on their stock levels
# We will create categories like 'Low Stock', 'Medium Stock', and 'High Stock'

# Defining stock level thresholds
low_stock_threshold = 20
high_stock_threshold = 80


# In[5]:


# Function to categorize stock levels
def categorize_stock_level(row):
    if row['Quantity in Stock'] <= low_stock_threshold:
        return 'Low Stock'
    elif row['Quantity in Stock'] >= high_stock_threshold:
        return 'High Stock'
    else:
        return 'Medium Stock'


# In[6]:


# Apply the function to categorize stock levels
inventory_df['Stock Category'] = inventory_df.apply(categorize_stock_level, axis=1)


# In[7]:


# Displaying the categorized inventory levels
inventory_df[['Item ID', 'Item Name', 'Quantity in Stock', 'Stock Category']].head()


# ### Identifying under or overstated products
# 
# We will compare the average restock quantity for each item with its current stock level

# In[8]:


# Calculating average restock quantity for each item
avg_restock_qty = restock_df.groupby('Item ID')['Quantity Added'].mean().reset_index()
avg_restock_qty.rename(columns={'Quantity Added': 'Average Restock Quantity'}, inplace=True)


# In[9]:


# Merging the average restock quantity with the current inventory levels
inventory_analysis_df = pd.merge(inventory_df, avg_restock_qty, on='Item ID', how='left')


# In[10]:


# Function to determine if the stock is understated or overstated
def stock_status(row):
    if row['Quantity in Stock'] > row['Average Restock Quantity'] * 2:
        return 'Overstated'
    elif row['Quantity in Stock'] < row['Average Restock Quantity'] / 2:
        return 'Understated'
    else:
        return 'Normal'


# In[11]:


# Apply the function
inventory_analysis_df['Stock Status'] = inventory_analysis_df.apply(stock_status, axis=1)


# In[12]:


# Displaying the results
inventory_analysis_df[['Item ID', 'Item Name', 'Quantity in Stock', 'Average Restock Quantity', 'Stock Status']].head()


# In[13]:


from collections import Counter


# ### Predicting future inventory needs
# 
# Estimating future requirements based on the frequency and quantity of past restocks
# 

# In[14]:


# Calculate the frequency of restocks for each item
restock_df['Restock Date'] = pd.to_datetime(restock_df['Restock Date'])
restock_frequency = restock_df.groupby('Item ID')['Restock Date'].agg(['count', 'min', 'max']).reset_index()
restock_frequency['Restock Period (Days)'] = (restock_frequency['max'] - restock_frequency['min']).dt.days / restock_frequency['count']
restock_frequency.rename(columns={'count': 'Restock Count'}, inplace=True)


# In[15]:


# Merge with the inventory analysis data
future_inventory_needs_df = pd.merge(inventory_analysis_df, restock_frequency[['Item ID', 'Restock Count', 'Restock Period (Days)']], on='Item ID', how='left')


# In[17]:


# Predicting when the next restock might be needed
# Assuming a similar consumption rate as observed in the past

from datetime import datetime

# Your existing code
future_inventory_needs_df['Days Until Next Restock'] = future_inventory_needs_df['Quantity in Stock'] / (future_inventory_needs_df['Average Restock Quantity'] / future_inventory_needs_df['Restock Period (Days)'])
future_inventory_needs_df['Predicted Restock Date'] = datetime.now() + pd.to_timedelta(future_inventory_needs_df['Days Until Next Restock'], unit='D')


# In[18]:


# Displaying the results
future_inventory_needs_df[['Item ID', 'Item Name', 'Quantity in Stock', 'Average Restock Quantity', 'Restock Period (Days)', 'Predicted Restock Date']].head()


# In[19]:


import matplotlib.pyplot as plt
import seaborn as sns


# In[20]:


# Setting the visual style for the plots
sns.set(style="whitegrid")

# 1. Stock Level Categories Pie Chart
stock_category_counts = inventory_df['Stock Category'].value_counts()
plt.figure(figsize=(8, 6))
plt.pie(stock_category_counts, labels=stock_category_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Stock Level Categories')
plt.show()


# In[21]:


# 2. Bar Chart of Inventory Levels
plt.figure(figsize=(12, 6))
top_items = inventory_df.head(10)  # Displaying top 10 items for simplicity
sns.barplot(x='Item ID', y='Quantity in Stock', hue='Stock Category', data=top_items)
plt.title('Top 10 Items Inventory Levels')
plt.xticks(rotation=45)
plt.show()


# In[22]:


# 3. Histogram of Restock Quantities
plt.figure(figsize=(10, 6))
sns.histplot(restock_df['Quantity Added'], bins=20, kde=True)
plt.title('Histogram of Restock Quantities')
plt.xlabel('Quantity Added')
plt.ylabel('Frequency')
plt.show()


# In[27]:


# 4. Heat Map of Inventory Turnover (using average restock frequency)
# For simplicity, we'll use the 'Restock Period (Days)' as a proxy for turnover

# Creating a pivot table for the heatmap
heatmap_data = future_inventory_needs_df.pivot("Item ID", "Category", "Restock Period (Days)")
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu")
plt.title('Heat Map of Inventory Turnover')
plt.xlabel('Category')
plt.ylabel('Item ID')
plt.show()


# In[28]:


# 5. Scatter Plot for Stock Status
# Plotting current stock levels against average restock quantity
plt.figure(figsize=(10, 6))
sns.scatterplot(data=future_inventory_needs_df, x='Average Restock Quantity', y='Quantity in Stock', hue='Stock Status')
plt.title('Scatter Plot of Stock Status')
plt.xlabel('Average Restock Quantity')
plt.ylabel('Current Stock Level')
plt.show()


# In[ ]:




