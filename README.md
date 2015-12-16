# qualpod
Generic interface for Qualtrics-Podio integrations.



## Creating a new integration

There are three steps to adding a new Qualtrics -> Podio integration.

1. Initializing the integration files
2. Mapping Qualtrics questions to Podio fields
  1. Retrieving Podio field information
  2. Retrieving Qualtrics question information
  3. Adding queston type information
3. Submitting the integration files

### 1. Initializing the integration files

* Create a new folder. We'll refer to this folder as `<folder_name>`.
* Create three empty files in your new folder:
  1. `<folder_name>_events.log`
    * This file will store a running log of the integration software's operations. This is extremely helpful for keeping track of errors as they come up.
  2. `<folder_name>_schema.csv`
    * This file contains the logic for the integration: it tells the software how to match Qualtrics data to Podio data.
  3. `<folder_name>_default_labels.csv`
    * This file helps the integration software provide smarter labels for default data fields. More on this below.

### 2. Mapping Qualtrics questions to Podio fields

* The first thing we need to do is make sure we know which Qualtrics question is paired with which Podio field. To do this, we'll set up a *schema* that makes an explicit mapping between those pairs.
* Open your schema file. *Note that the schema file always needs to be saved in .csv format, otherwise it won't function properly.* You can open the file in Excel, WordEdit, Notepad, or any other editing software; whatever you're most familiar with will work. This tutorial will assume you're using a basic text editor.
* To get started, here are a few example lines from a theoretical integration:
  ```
  business-title,Q1,text
  business-type,Q4,category
  customer-types,Q5~8,multiple
  ```
* Note that each line has four fields. Those fields correspond to the following:
  1. Podio field identifier, e.g. `event-title` or `event-description`
  2. Qualtrics question identifier, e.g. `Q14` or `Q12_TEXT`
  3. Data type, e.g. `text` or `category`
  4. Default field value, e.g. `1` or `NA`
* For each Podio field you want to fill with data from Qualtrics, you need to create a new line that specifies how each of these fields matches up.
* Also notice that each data type has a slightly different notation. We'll go over each of these in more detail below.

#### 2a. Retrieving Podio field information

* In the first column of the integration schema file, we're going to identify the Podio fields we want to integrate.
* Navigate to the Podio app you're going to integrate, click on the wrench icon on the left sidebar, and scroll down to 'Developer'.
* In the first column of your schema file, type in the **External ID** of each field you want to automatically populate with data from Qualtrics survey responses.
  * If you have a field you want to use to capture special notes or other questions from the Qualtrics form not captured in their own distinct Podio fields, *list that field last in the schema file*. We'll review how to set up these 'default' fields shortly.
  * Not every field on Podio needs to be automatically populated. However, the software does assume that every question response received on Qualtrics will be either explicitly routed to somewhere on the Podio app or otherwise discarded.
* Our schema file should now look something like this. We'll stick with our theoretical business example to keep things simple:
  ```
  business-title
  homepage-url
  founding-date
  business-type
  customer-types
  customer-type-descriptions
  business-info
  ```
* As a last step, take note of the **Podio App ID** located at the top of the Developer page. This is usually an 8-digit number. We'll need this identifier later on in the integration process so that we can tell the integration software which Podio app we're working with.

#### 2b. Retrieving Qualtrics question information

* Next, we're going to match these Podio fields with the Qualtrics questions that we want to feed into them.
* Navigate to the Qualtrics survey you're going to integrate, and go to the Edit Survey page.
* In the second column of your schema file, type in the **Question ID** that you want to link to the corresponding Podio app field for that row. For our hypothetical business app, our schema file might now look something like this:
  ```
  business-title,Q1
  homepage-url,Q2
  founding-date,Q3
  business-type,Q4
  customer-types,Q5
  customer-needs,Q6
  business-info,default
  ```
* You'll also need to take note of the **Qualtrics Survey ID** for this survey, just like we did with the Podio App ID. You can get this identifier by clicking "Distribute Survey" and looking at the survey URL. The Survey ID is the part of the URL that looks like &SID=`<SURVEY_ID>`. It should be something like `SV_3hsih4USJx9wsDX0`.
* The last thing we're going to need is a raw export of an example response for your survey. This software package contains a service that can pull that information for you:
  1. Submit a sample response through your survey. Fill out as many questions as possible, especially if your survey has branching logic; this will help you get a better sense for how the data is formatted.
  2. Make sure your survey is shared with the VPOL group on Qualtrics.
  3. Go to `stanford.edu/~atkindel/vptl_integrations/survey_examiner.html`.
  4. Enter your survey ID into the webform and click **Submit**.
  5. The page will display the raw survey data for your sample response. You'll need this data shortly.

#### 2c. Adding question type information

* The third column of our schema file contains a label corresponding to the type of data we're moving between Qualtrics and Podio. In some cases, we'll also need to edit the second column to give the software a bit more information about how Qualtrics labels its data.
* This integration software supports seven different data types:
  1. `text`
  2. `link`
  3. `date`
  4. `category`
  5. `multiple`
  6. `multitext`
  7. `default`
* Below, we'll go into a little more detail here on how to handle each data type, in order of increasing complexity. For each data type, there are also some notes on how to set up your Podio app and Qualtrics survey so that they work nicely together.

  ##### 1. `text`
  * `Text` fields are the easiest case to work with. Here, we just need to tell the schema file to expect text input, like so:
  ```
  business-title,Q1,text
  ```
  * Podio field type: `text`
  * Qualtrics question type: Text entry

  ##### 2. `link`
  * `Link` fields allow you to embed URLs in your Podio app entry. These work similarly to text fields:
  ```
  business-title,Q1,text
  homepage-url,Q2,link
  ```
  * Podio field type: `embed`
  * Qualtrics question type: Text entry.
    * **Note**: The software will discard responses to this question type that aren't URLs if they're labeled as `link` in your schema file.

  ##### 3. `date`
  * `Date` fields work a lot like the above two data types:
  ```
  business-title,Q1,text
  homepage-url,Q2,link
  founding-date,Q3,date
  ```
  * Podio field type: `date`
  * Qualtrics question type: Text entry.
    * Additionally, you need to enable *content validation* for this question to constrain user responses to the date format **yyyy/mm/dd**. The software assumes that dates are formatted as such.

  ##### 4. `category`
  * `Category` fields are labeled similarly:
  ```
  business-title,Q1,text
  homepage-url,Q2,link
  founding-date,Q3,date
  business-type,Q4,category
  ```
  * Podio field type: `category`.
    * This field should be set up to only allow a *single choice*.
  * Qualtrics question type: Multiple choice.
    * For fields with data type `category`, make sure that the options on Podio are in the same order as they appear on the Qualtrics survey when you create the Podio app. The integration software assumes the ordering is identical.
  * **Note**: Some of these questions have a text field associated with one or more of the possible responses. You can use the raw Qualtrics export data we collected above to identify these text fields and link them to Podio text fields as needed. For example, **Q7_TEXT** is the text field associated with **Q7** on Qualtrics.

  ##### 5. `multiple`
  * This is where it starts to get a little tricky. `Multiple`-type fields need a little extra information about the Qualtrics question you're feeding them as a result of how Qualtrics stores data about checkbox-type questions.
  * To accurately determine this information, we'll need to look at our sample export of the raw Qualtrics data.
  * For this question number, you'll see a set of question responses in the raw data that correspond to whether the user checked the n-th box for that question. So for our hypothetical question 5, if a user checked boxes 2 and 3 on the Qualtrics survey and question 5 had 6 possible choices, the data will look like the following:
  ```
  "Q5_1": ""
  "Q5_2": "1"
  "Q5_3": "1"
  "Q5_4": ""
  "Q5_5": ""
  "Q5_6": ""
  ```
  * Take the highest choice number and add it to the second column of your schema file, separated from the Question ID by a tilde ('~'). Then, add the `multiple` label to the third column. For example:
  ```
  business-title,Q1,text
  homepage-url,Q2,link
  founding-date,Q3,date
  business-type,Q4,category
  customer-types,Q5~6,multiple
  ```
  * **Note**: Sometimes, the choices are numbered erratically, e.g. the choices might be numbered 1,2,3,7,8 rather than 1,2,3,4,5. If this shows up in your Qualtrics export data, you should delete that question, remake it, and check another export to ensure that the numbering is continuous. Otherwise, the Podio app runs into trouble determining which choice numbers correspond.
  * Podio field type: `category`
    * This field should be set up to allow *multiple choices*.
  * Qualtrics question type: Multiple choice.
    * For fields with data type `multiple`, make sure that the options on Podio are in the same order as they appear on the Qualtrics survey when you create the Podio app. The integration software assumes the ordering is identical.

  ##### 6. `multitext`
  * Occasionally, you might have a single multiple choice question where multiple boxes may be checked and where each box has an associated text field. You can redirect these to individual text fields or capture them in your default field (more on that below), or you can concatenate them into one field.
  * Take a look at your Qualtrics data. Questions that work with this data type will have something similar to the following:
  ```
  "Q6_1": ""
  "Q6_2": "1"
  "Q6_3": ""
  "Q6_4": "1"
  "Q6_1_TEXT": ""
  "Q6_2_TEXT": "Example text."
  "Q6_3_TEXT": ""
  "Q6_4_TEXT": "Example text."
  ```
  * To route these text fields to a single Podio field, list the choice numbers with associated text fields in column two, separated from each other by dashes and from the question ID by a tilde. For example, the above example question would look like the following:
  ```
  business-title,Q1,text
  homepage-url,Q2,link
  founding-date,Q3,date
  business-type,Q4,category
  customer-types,Q5~6,multiple
  customer-needs,Q6~1-2-3-4,multitext
  ```
  * Podio field type: `text`
  * Qualtrics question(s) type: Text entry.

  ##### 7. `default`
  * Each integration schema should have a default field on Podio to capture certain types of input from Qualtrics. Default fields are good for unpredictably formatted text responses (e.g. estimates, freeform responses) or for when you want human-readable access to data but don't need to interact with it systematically.
    * The default field does not work well with category-type data or answers to multiple-choice questions.
  * *On the last line of your schema file*, use the following notation to identify your default field:
  ```
  business-title,Q1,text
  homepage-url,Q2,link
  founding-date,Q3,date
  business-type,Q4,category
  customer-types,Q5~6,multiple
  customer-needs,Q6~1-2-3-4,multitext
  business-info,default,default
  ```
  * The last thing we need to do is tell the software what data you want to route into the default field. To do that, we'll put together a mapping between the Qualtrics questions we want to capture and the labels we want to give those questions in our default field. We'll do this in our `default_labels` file.
  * In first column of the `default_labels` file, list the Qualtrics question IDs you want to capture in your default field:
  ```
  Q7
  Q8
  Q9
  Q10
  ```
  * In the second column, give each question a short descriptive label.
  ```
  Q7,Founder
  Q8,City
  Q9,Mission statement
  Q10,Phone number
  ```

### 3. Submitting the integration files

* Email the folder containing your integration files to Alex Kindel. Include a note with the following information:
  * A simple name for the integration (e.g. 'VPTL Events')
  * Podio app ID
  * Qualtrics survey ID
  * A description of when or how often you'd like the integration to run (e.g. every morning at 6am, twice daily, every Friday at 8pm).
