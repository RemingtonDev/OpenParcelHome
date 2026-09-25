// Original wrapper around Google's Apache-2.0 apksig library. Does not execute APK code.
import com.android.apksig.ApkVerifier;
import java.io.File;
import java.security.MessageDigest;
import java.util.HexFormat;

public class VerifyApk {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("Supply one APK path");
        var result = new ApkVerifier.Builder(new File(args[0])).build().verify();
        System.out.println("verified=" + result.isVerified());
        System.out.println("v1=" + result.isVerifiedUsingV1Scheme());
        System.out.println("v2=" + result.isVerifiedUsingV2Scheme());
        System.out.println("v3=" + result.isVerifiedUsingV3Scheme());
        System.out.println("v3.1=" + result.isVerifiedUsingV31Scheme());
        System.out.println("v4=" + result.isVerifiedUsingV4Scheme());
        System.out.println("lineage_present=" + (result.getSigningCertificateLineage() != null));
        for (var cert : result.getSignerCertificates()) {
            System.out.println("signer_sha256=" + HexFormat.of().formatHex(
                MessageDigest.getInstance("SHA-256").digest(cert.getEncoded())));
        }
        for (var issue : result.getAllErrors()) System.out.println("error=" + issue);
        for (var issue : result.getWarnings()) System.out.println("warning=" + issue);
        for (var signer : result.getV1SchemeSigners())
            for (var issue : signer.getWarnings()) System.out.println("v1_warning=" + issue);
        for (var signer : result.getV2SchemeSigners())
            for (var issue : signer.getWarnings()) System.out.println("v2_warning=" + issue);
        for (var signer : result.getV3SchemeSigners())
            for (var issue : signer.getWarnings()) System.out.println("v3_warning=" + issue);
        if (!result.isVerified()) System.exit(1);
    }
}
