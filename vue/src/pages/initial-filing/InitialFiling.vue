<template>
  <div class="question-well-border-less" id="app">
    <template v-if="signingLocation === 'In-person' || signingLocationYou === 'In-person'">
      <div>
        <div>
          <p>The Notice of Joint Family Claim Form (F1) will be automatically filed for you.</p>
        </div>
        <div>
          <p>Upload a scan of your Proof of Marriage <i class="fa fa-question-circle"></i>
            <Uploader/>
          </p>
        </div>
        <div>
          <p>Scan and upload the sworn Affidavit of Interpreter Form <i class="fa fa-question-circle"></i>
            <Uploader/>
          </p>
        </div>
        <div>
          <p>Complete, scan and upload the Registration of Divorce Proceedings <i class="fa fa-question-circle"></i> form
            <Uploader/>
          </p>
        </div>
      </div>
    </template>
    <template v-else-if="signingLocationYou === 'Virtual' && signingLocationSpouse === 'In-person'">
      <div>
          <p>The following forms will be automatically filed for you:</p>
          <ul>
            <li>Notice of Joint Family Claim Form (F1)</li>
            <li>Requisition Form (F35)</li>
            <li>Certificate of Pleadings Form (F36)</li>
          </ul>
          <p>The following forms will be submitted for you but require swearing / affirming <i class="fa fa-question-circle"></i> before filing (see next step for details)</p>
          <ul>
            <li>Child Support Affidavit (F37)</li>
            <li>Affidavit - Desk Order Divorce Form (F38)</li>
          </ul>
          <div class="question-well-border-less">
            <div>
              <p>Upload a scan of your Proof of Marriage <i class="fa fa-question-circle"></i>
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Scan and upload the sworn Affidavit of Interpreter Form <i class="fa fa-question-circle"></i>
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Upload the signed and scanned Draft Final Order Form (F52)
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Upload the signed and scanned Electronic Filing Statement (F96) for You
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Complete, scan and upload the Registration of Divorce Proceedings form
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Complete, scan and upload the Agreement as to Annual Income (F9) form
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Complete, scan and upload the Identification of Applicant (VSA 512) for You
                <Uploader/>
              </p>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div>
          <p>The following forms will be automatically filed for you:</p>
          <ul>
            <li>Notice of Joint Family Claim Form (F1)</li>
            <li>Requisition Form (F35)</li>
            <li>Certificate of Pleadings Form (F36)</li>
          </ul>
          <p>The following forms will be submitted for you but require swearing / affirming <i class="fa fa-question-circle"></i> before filing (see next step for details)</p>
          <ul>
            <li>Child Support Affidavit (F37)</li>
            <li>Affidavit - Desk Order Divorce Form (F38)</li>
          </ul>
          <div class="question-well-border-less">
            <div>
              <p>Upload a scan of your Proof of Marriage <i class="fa fa-question-circle"></i>
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Scan and upload the sworn Affidavit of Interpreter Form <i class="fa fa-question-circle"></i>
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Upload the signed and scanned Draft Final Order Form (F52)
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Upload the signed and scanned Electronic Filing Statement (F96) for You
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Upload the signed and scanned Electronic Filing Statement (F96) for Your Spouse
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Complete, scan and upload the Registration of Divorce Proceedings form
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Complete, scan and upload the Agreement as to Annual Income (F9) form
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Complete, scan and upload the Identification of Applicant (VSA 512) for You
                <Uploader/>
              </p>
            </div>
            <div>
              <p>Complete, scan and upload the Identification of Applicant (VSA 512) for Your Spouse
                <Uploader/>
              </p>
            </div>
          </div>
        </div>
      </template>
  </div>
</template>

<script>
import Uploader from '../../components/Uploader.vue'

export default {
  name: 'App',
  components: {
    Uploader
  },
  props: {
    signingLocation: String,
    signingLocationYou: String,
    signingLocationSpouse: String
  }
}
</script>

<style>
</style>