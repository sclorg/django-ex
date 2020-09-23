<template>
  <div class="question-well-border-less" id="app">
    <template v-if="signingLocation === 'In-person' || signingLocationYou === 'In-person'">
      <div>
        <div>
          <p>The Notice of Joint Family Claim Form (F1) will be automatically filed for you.</p>
        </div>
        <div>
          <!-- MC - Marriage Certificate -->
          <Uploader doc-type="MC"/>
        </div>
        <div>
          <!-- AFTL - Affidavit of Translator -->
          <Uploader doc-type="AFTL"/>
        </div>
        <div>
          <!-- RDP - Registration of Divorce Proceeding -->              
          <Uploader doc-type="RDP"/>
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
          <div>
            <!-- MC - Marriage Certificate -->              
            <Uploader doc-type="MC"/>
          </div>
          <div>
            <!-- AFTL - Affidavit of Translator -->              
            <Uploader doc-type="AFTL"/>
          </div>
          <div>
            <!-- OFI - Final Order -->
            <Uploader doc-type="OFI"/>
          </div>
          <div>
            <!-- EFSS - Electronic Filing Statement - Supreme -->          
            <Uploader doc-type="EFSS" :party="1"/>
          </div>
          <div>
            <!-- RDP - Registration of Divorce Proceeding -->              
            <Uploader doc-type="RDP"/>
          </div>
          <div>
            <!-- AAI - Agreement as to Annual Income -->
            <Uploader doc-type="AAI"/>
          </div>
          <div>
            <!-- NCV – Name Change Form – Vital Statistics -->
            <Uploader doc-type="NCV" :party="1"/>
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
          <div>
            <!-- MC - Marriage Certificate -->              
            <Uploader doc-type="MC"/>
          </div>
          <div>
            <!-- AFTL - Affidavit of Translator -->              
            <Uploader doc-type="AFTL"/>
          </div>
          <div>
            <!-- OFI - Final Order -->
            <Uploader doc-type="OFI"/>
          </div>
          <div>
            <!-- EFSS - Electronic Filing Statement - Supreme -->          
            <Uploader doc-type="EFSS" :party="1"/>
          </div>
          <div>
            <!-- EFSS - Electronic Filing Statement - Supreme -->
            <Uploader doc-type="EFSS" :party="2"/>
          </div>
          <div>
            <!-- RDP - Registration of Divorce Proceeding -->              
            <Uploader doc-type="RDP"/>
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