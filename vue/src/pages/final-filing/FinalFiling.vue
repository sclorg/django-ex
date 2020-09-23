<template>
  <div id="app">
    <div class="question-well-border-less" v-if="signingLocation === 'Virtual'">
      <div>
        <!-- CSA - Child Support Affidavit -->            
        <Uploader doc-type="CSA"/>
      </div>
      <div>
        <!-- AFDO - Affidavit - Desk Order Divorce -->            
        <Uploader doc-type="AFDO"/>
      </div>
    </div>
    <div class="question-well-border-less" v-else-if="signingLocationYou === 'Virtual' && signingLocationSpouse === 'Virtual'">
      <div>
        <!-- CSA - Child Support Affidavit -->
        <Uploader doc-type="CSA" :party="1"/>
      </div>
      <div>
        <!-- AFDO - Affidavit - Desk Order Divorce -->
        <Uploader doc-type="AFDO" :party="1"/>
      </div>
      <div>
        <!-- CSA - Child Support Affidavit -->
        <Uploader doc-type="CSA" :party="2"/>        
      </div>
      <div>
        <!-- AFDO - Affidavit - Desk Order Divorce -->            
        <Uploader doc-type="AFDO" :party="2"/>
      </div>
    </div>
    <template v-else-if="howToFile === 'Online'">
      <div class="question-well-border-less" v-if="signingLocation.length || (signingLocationYou.length && signingLocationSpouse.length)">
        <p>Missing a form required on this page? Check the <a :href="printFormUrl">Review Forms</a> step.</p>
        <p>The following forms will be automatically filed for you:</p>
        <ul>
          <li>Requisition Form (F35)</li>
          <li>Certificate of Pleadings Form (F36)</li>
        </ul>
        <div>
          <!-- CSA - Child Support Affidavit -->
          <Uploader doc-type="CSA"/>
        </div>
        <div>
          <!-- AFDO - Affidavit - Desk Order Divorce -->
          <Uploader doc-type="AFDO"/>
        </div>
        <div>
          <!-- OFI - Final Order -->
          <Uploader doc-type="OFI"/>
        </div>
        <div>
          <!-- EFSS - Electronic Filing Statement - Supreme -->          
          <Uploader doc-type="EFSS"
            :party="1"
            post-text=" - For You"/>
        </div>
        <div>
          <!-- EFSS - Electronic Filing Statement - Supreme -->
          <Uploader doc-type="EFSS" :party="2"/>
        </div>
        <div>
          <!-- AAI - Agreement as to Annual Income -->
          <Uploader doc-type="AAI"/>
        </div>
        <div>
          <!-- NCV – Name Change Form – Vital Statistics -->
          <Uploader doc-type="NCV" :party="1"/>
        </div>
        <div>
          <!-- NCV – Name Change Form – Vital Statistics -->
          <Uploader doc-type="NCV" :party="2"/>
        </div>
      </div>
      <div class="question-well-border-less" v-else>
        <h2>You need to select a signing method in the <a :href="signFileOptionsUrl">Signing & Filing Options</a>
          step.</h2>
      </div>
    </template>
    <template v-else-if="howToSign === 'Together'">
      <div>
        <p>Staple each form together and then fasten all forms with a paper clip, in the following order:</p>
        <ul>
          <li>Notice of Joint Family Claim Form (F1)</li>
          <li>Requisition Form (F35)</li>
          <li>Draft Final Order Form (F52)</li>
          <li>Certificate of Pleadings Form (F36)</li>
          <li>Child Support Affidavit (F37) signed by claimants</li>
          <li>Affidavit Desk Order Divorce (F38) signed by both claimants</li>
          <li>Agreement as to Annual Income (F9)</li>
        </ul>
        <p>Also ensure you bring the following additional documentation:</p>
        <ul>
          <li>Proof of marriage</li>
          <li>Registration of Joint Divorce Proceedings (JUS280)</li>
          <li>Identification of Applicant (VSA 512) for Claimant 1 ([Name])</li>
          <li>Identification of Applicant (VSA 512) for Claimant 2 ([Name])</li>
          <li>Agreement as to Annual Income (F9)</li>
        </ul>
        <p>If you have other court orders or a written separation agreement, they should also be attached to your Affidavit — Desk Order Divorce
          Form</p>
        <p>(F38). Note that these agreements or orders must not contradict what's in your divorce application.</p>
        <p>You have indicated that you will file at the following court registry:</p>
        <p>[City]</p>
        <p>[Address]</p>
        <p>[Postal Code]</p>
        <p>Once sign / sworn and filed, you will receive a Court Filing Number <i class="fa fa-question-circle"></i>. This number will be used if you need to file any
          additional documentation.</p>
      </div>
    </template>
    <template v-else-if="howToSign === 'Separately'">
      <div class="question-well-border-less">
        <p>Staple each form together and then fasten all forms with a paper clip, in the following order:</p>
        <ul>
          <li> Notice of Joint Family Claim Form (F1)</li>
          <li> Requisition Form (F35)</li>
          <li> Draft Final Order Form (F52)</li>
          <li> Certificate of Pleadings Form (F36)</li>
          <li> Child Support Affidavit (F37) signed by you</li>
          <li> Affidavit Desk Order Divorce (F38) signed by you</li>
          <li> Agreement as to Annual Income (F9)</li>
        </ul>
        <br>
        <p>Also ensure you bring the following additional documentation:</p>
        <ul>
          <li> Proof of marriage</li>
          <li> Registration of Joint Divorce Proceedings (JUS280)</li>
          <li> Identification of Applicant (VSA 512) for Claimant 1 ([Name])</li>
          <li> Agreement as to Annual Income (F9)</li>
        </ul>
        <p>If you have other court orders or a written separation agreement, they should also be attached to your Affidavit — Desk Order Divorce
          Form</p>
        <p>(F38). Note that these agreements or orders must not contradict what's in your divorce application.</p>
        <p>You have indicated that you will file at the following court registry:</p>
        <p>[City]</p>
        <p>[Address]</p>
        <p>[Postal Code]</p>
        <p>Once sign / sworn and filed, you will receive a Court Filing Number <i class="fa fa-question-circle"></i>. This number will be used if you need to file any
          additional documentation.</p>
        <h2>Spousal Documentation Requirements</h2>
        <p>The following sworn / affirmed affidavits still remains to be filed:</p>
        <ul>
          <li> Child Support Affidavit (F37) - signed by your spouse</li>
          <li> Affidavit - Desk Order Divorce Form (F38) - signed by your spouse</li>
          <li> Identification of Applicant (VSA 512) - for your Spouse</li>
        </ul>
        <p>Either you or your spouse must file this documentation using the Court Filing Number <i class="fa fa-question-circle"></i> that you received via e-mail. If you have
          not received a Court Filing Number then please check to the Wait for Court Filing Number step.</p>
        <p>You have indicated that you will file at the following court registry:</p>
        <p>[City]</p>
        <p>[Address]</p>
        <p>[Postal Code]</p>
      </div>
    </template>
  </div>
</template>

<script>
import Uploader from '../../components/Uploader/Main.vue';

export default {
  name: 'App',
  components: {
    Uploader
  },
  props: {
    signingLocation: String, 
    signingLocationYou: String, 
    signingLocationSpouse: String, 
    howToSign: String, 
    howToFile: String, 
    signFileOptionsUrl: String, 
    printFormUrl: String,
    proxyRootPath: String
  }
}
</script>

<style scoped lang="scss">
  .question-well-border-less {
    padding: 10px 20px 30px 20px;
    background-color: #F2F2F2;
    border: 1px solid #DDD;
    border-radius: 6px;
  }
</style>